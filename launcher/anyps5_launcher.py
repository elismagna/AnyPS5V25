import base64
import collections
import json
import os
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import launcher_core

LOG_LINES = 2000


def ui_dir():
    bundled = Path(getattr(sys, "_MEIPASS", ""))
    if bundled and (bundled / "ui" / "index.html").is_file():
        return bundled / "ui"
    return Path(__file__).resolve().parent / "ui"


def reveal(path):
    path = str(path)
    if launcher_core.WINDOWS:
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class Api:
    def __init__(self, library):
        self.library = library
        self.runtime = launcher_core.Runtime(library, on_line=self._line, on_exit=self._exit)
        self.window = None
        self.logs = collections.defaultdict(lambda: collections.deque(maxlen=LOG_LINES))
        self.busy = {}
        self.pending = collections.defaultdict(list)
        self.lock = threading.Lock()
        self.flusher = threading.Thread(target=self._flush_loop, daemon=True)
        self.flusher.start()

    def attach(self, window):
        self.window = window

    def _emit(self, event):
        if self.window is None:
            return
        try:
            self.window.evaluate_js(f"window.anyps5 && window.anyps5.push({json.dumps(event)})")
        except Exception:
            pass

    def _line(self, game_id, line):
        self._record(game_id, line)

    def _record(self, game_id, line):
        with self.lock:
            self.logs[game_id].append(line)
            self.pending[game_id].append(line)
        try:
            game = self.library.get(game_id)
            path = self.runtime.log_path(game)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8", errors="replace") as stream:
                stream.write(line + "\n")
        except (KeyError, OSError):
            pass

    def _flush_loop(self):
        while True:
            time.sleep(0.15)
            with self.lock:
                batches = {game_id: lines for game_id, lines in self.pending.items() if lines}
                self.pending.clear()
            for game_id, lines in batches.items():
                self._emit({"type": "log", "id": game_id, "lines": lines})

    def _exit(self, game_id, code):
        self._record(game_id, f"Exited with code {code}")
        self._emit({"type": "status", "id": game_id, "status": self._status_of(game_id), "code": code})

    def _status_of(self, game_id):
        if self.busy.get(game_id):
            return self.busy[game_id]
        try:
            return self.runtime.status(self.library.get(game_id))
        except KeyError:
            return "gone"

    def _game_view(self, game):
        view = dict(game)
        view["status"] = self._status_of(game["id"])
        view["game_dir"] = str(self.runtime.game_dir(game))
        view["intel_effective"] = self.runtime.use_intel(game)
        return view

    def _guard(self, action):
        try:
            return {"ok": True, "result": action()}
        except Exception as error:
            traceback.print_exc()
            return {"ok": False, "error": str(error)}

    def bootstrap(self):
        return self._guard(lambda: {
            "games": [self._game_view(game) for game in self.library.games()],
            "settings": dict(self.library.settings),
            "tooling": self.runtime.tooling.status(),
            "home": str(self.library.home),
            "platform": launcher_core.platform_name(),
            "frozen": launcher_core.is_frozen(),
        })

    def tooling(self):
        return self._guard(self.runtime.tooling.status)

    def pick_folder(self):
        def pick():
            if self.window is None:
                return None
            import webview

            result = self.window.create_file_dialog(webview.FileDialog.FOLDER)
            return result[0] if result else None

        return self._guard(pick)

    def pick_file(self):
        def pick():
            if self.window is None:
                return None
            import webview

            result = self.window.create_file_dialog(webview.FileDialog.OPEN)
            return result[0] if result else None

        return self._guard(pick)

    def add_game(self, path=None):
        def add():
            folder = path
            if not folder:
                picked = self.pick_folder()
                folder = picked.get("result") if picked.get("ok") else None
            if not folder:
                return None
            folder = Path(folder)
            if folder.is_file():
                folder = folder.parent
            game = self.library.add(folder)
            return self._game_view(game)

        return self._guard(add)

    def remove_game(self, game_id, delete_files=True):
        def remove():
            game = self.library.get(game_id)
            if delete_files:
                self.runtime.forget(game)
            self.library.remove(game_id)
            with self.lock:
                self.logs.pop(game_id, None)
                self.pending.pop(game_id, None)
            return game_id

        return self._guard(remove)

    def update_game(self, game_id, fields):
        return self._guard(lambda: self._game_view(self.library.update(game_id, **dict(fields))))

    def update_settings(self, fields):
        return self._guard(lambda: {"settings": self.library.update_settings(**dict(fields)), "tooling": self.runtime.tooling.status()})

    def play(self, game_id):
        return self._start(game_id, launch=True)

    def rebuild(self, game_id):
        return self._start(game_id, launch=False)

    def _start(self, game_id, launch):
        def start():
            game = self.library.get(game_id)
            if self.busy.get(game_id):
                raise RuntimeError("Please wait, this game is still being prepared")
            if self.runtime.running(game_id):
                raise RuntimeError("This game is already running")
            self.busy[game_id] = "converting"
            self._emit({"type": "status", "id": game_id, "status": "converting"})
            threading.Thread(target=self._work, args=(game, launch), daemon=True).start()
            return "converting"

        return self._guard(start)

    def _work(self, game, launch):
        game_id = game["id"]
        log = lambda line: self._record(game_id, line)
        try:
            if launch:
                self.runtime.play(game, log)
            else:
                self.runtime.convert(game, log)
        except Exception as error:
            log(f"Error: {error}")
            self.busy.pop(game_id, None)
            self._emit({"type": "status", "id": game_id, "status": self._status_of(game_id), "error": str(error)})
            return
        self.busy.pop(game_id, None)
        self._emit({"type": "status", "id": game_id, "status": self._status_of(game_id)})

    def stop(self, game_id):
        return self._guard(lambda: self.runtime.stop(game_id))

    def log(self, game_id):
        with self.lock:
            return {"ok": True, "result": list(self.logs.get(game_id, ()))}

    def clear_log(self, game_id):
        with self.lock:
            self.logs.pop(game_id, None)
        return {"ok": True, "result": True}

    def icon(self, game_id):
        def read():
            game = self.library.get(game_id)
            icon = game.get("icon")
            if not icon or not Path(icon).is_file():
                return None
            data = Path(icon).read_bytes()
            return "data:image/png;base64," + base64.b64encode(data).decode("ascii")

        return self._guard(read)

    def open_folder(self, game_id):
        return self._guard(lambda: reveal(self.library.get(game_id)["folder"]))

    def open_game_dir(self, game_id):
        def open_dir():
            directory = self.runtime.game_dir(self.library.get(game_id))
            directory.mkdir(parents=True, exist_ok=True)
            reveal(directory)

        return self._guard(open_dir)

    def open_home(self):
        def open_home():
            self.library.home.mkdir(parents=True, exist_ok=True)
            reveal(self.library.home)

        return self._guard(open_home)

    def quit(self):
        self.runtime.stop_all()
        if self.window is not None:
            self.window.destroy()
        return {"ok": True, "result": True}


def main():
    import webview

    library = launcher_core.Library()
    api = Api(library)
    window = webview.create_window(
        "AnyPS5",
        str(ui_dir() / "index.html"),
        js_api=api,
        width=1180,
        height=760,
        min_size=(860, 560),
        background_color="#0b0d12",
        text_select=False,
    )
    api.attach(window)
    window.events.closing += lambda *args: api.runtime.stop_all()
    webview.start(debug="--debug" in sys.argv)
    api.runtime.stop_all()


if __name__ == "__main__":
    main()
