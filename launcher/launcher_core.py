import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

WINDOWS = os.name == "nt"
MODULE_DIRECTORIES = ("sce_module", "sce_modules", "prx")
ELF_MAGIC = b"\x7fELF"
ELF_NAMES = ("eboot.bin", "eboot.elf", "eboot.self")
OUTPUT_NAME = "app.exe" if WINDOWS else "app.elf"
INTEL_CHOICES = ("auto", "on", "off")


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def install_dir():
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def repository_root():
    return Path(__file__).resolve().parent.parent


def default_home():
    override = os.environ.get("ANYPS5_LAUNCHER_HOME")
    if override:
        return Path(override)
    if WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "AnyPS5"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AnyPS5"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "anyps5"


def host_is_intel(vendor=None):
    if vendor is None:
        vendor = platform.processor() or ""
        if not WINDOWS:
            cpuinfo = Path("/proc/cpuinfo")
            if cpuinfo.is_file():
                vendor += cpuinfo.read_text(errors="replace")[:4096]
    return "GenuineIntel" in vendor


def is_elf(path):
    try:
        with open(path, "rb") as stream:
            return stream.read(4) == ELF_MAGIC
    except OSError:
        return False


def read_title(root):
    param = root / "sce_sys" / "param.json"
    title, title_id, version = None, None, None
    if param.is_file():
        try:
            data = json.loads(param.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            data = {}
        if isinstance(data, dict):
            title_id = data.get("titleId") if isinstance(data.get("titleId"), str) else None
            version = data.get("masterVersion") if isinstance(data.get("masterVersion"), str) else None
            localized = data.get("localizedParameters")
            if isinstance(localized, dict):
                default = localized.get("defaultLanguage")
                languages = [default, "en-US"] + sorted(key for key in localized if isinstance(key, str))
                for language in languages:
                    entry = localized.get(language) if isinstance(language, str) else None
                    if isinstance(entry, dict) and isinstance(entry.get("titleName"), str) and entry["titleName"].strip():
                        title = entry["titleName"].strip()
                        break
            if title is None and isinstance(data.get("titleName"), str) and data["titleName"].strip():
                title = data["titleName"].strip()
    return title, title_id, version


def find_executable(root):
    for name in ELF_NAMES:
        for candidate in sorted(root.iterdir()):
            if candidate.is_file() and candidate.name.lower() == name and is_elf(candidate):
                return candidate
    elves = [candidate for candidate in sorted(root.iterdir()) if candidate.is_file() and is_elf(candidate)]
    return elves[0] if len(elves) == 1 else None


def module_directories(root):
    return [root / name for name in MODULE_DIRECTORIES if (root / name).is_dir()]


def scan_game(folder, depth=2):
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a folder: {root}")
    candidates = [root]
    for level in range(1, depth + 1):
        for entry in sorted(root.glob("/".join(["*"] * level))):
            if entry.is_dir():
                candidates.append(entry)
    for candidate in candidates:
        try:
            executable = find_executable(candidate)
        except OSError:
            continue
        if executable is not None:
            root = candidate
            break
    else:
        raise ValueError(f"No PS5 executable (eboot.bin) found in {root} or its subfolders")
    modules = module_directories(root)
    problems = []
    if not modules:
        problems.append("No sce_module, sce_modules or prx folder beside the executable; the relinker needs the game's bundled modules")
    if (root / "sce_module").is_dir() and (root / "sce_modules").is_dir():
        problems.append("Both sce_module and sce_modules exist; keep only one")
    title, title_id, version = read_title(root)
    icon = root / "sce_sys" / "icon0.png"
    return {
        "folder": str(root),
        "executable": executable.name,
        "modules": [directory.name for directory in modules],
        "title": title or root.name,
        "title_id": title_id,
        "version": version,
        "icon": str(icon) if icon.is_file() else None,
        "problems": problems,
    }


def platform_name():
    return "windows" if WINDOWS else "linux"


class Tooling:
    def __init__(self, settings):
        self.settings = settings

    def relinker_name(self):
        return "relinker.exe" if WINDOWS else "relinker"

    def relinker_candidates(self):
        configured = self.settings.get("relinker")
        if configured:
            yield Path(configured)
        environment = os.environ.get("ANYPS5_RELINKER")
        if environment:
            yield Path(environment)
        yield install_dir() / self.relinker_name()
        root = repository_root()
        yield root / f"AnyPS5-{platform_name()}" / self.relinker_name()
        yield root / "build" / "core" / "relinker" / self.relinker_name()
        found = shutil.which("relinker")
        if found:
            yield Path(found)

    def relinker(self):
        for candidate in self.relinker_candidates():
            if candidate.is_file():
                return candidate.resolve()
        return None

    def libs_candidates(self):
        configured = self.settings.get("libs")
        if configured:
            yield Path(configured)
        relinker = self.relinker()
        if relinker is not None:
            yield relinker.parent / "libs"
        yield install_dir() / "libs"
        yield repository_root() / "build" / "core" / "libs" / "libs"

    def libs(self):
        for candidate in self.libs_candidates():
            if candidate.is_dir() and any(candidate.glob("*.prx")):
                return candidate.resolve()
        return None

    def relinker_command(self):
        relinker = self.relinker()
        if relinker is None:
            raise RuntimeError("relinker was not found. Put relinker next to the launcher, build it, or choose it in Settings")
        return [str(relinker)]

    def status(self):
        relinker = self.relinker()
        libs = self.libs()
        version = None
        commit = install_dir() / "COMMIT.txt"
        if commit.is_file():
            version = commit.read_text(errors="replace").strip()[:12] or None
        return {
            "relinker": str(relinker) if relinker else None,
            "libs": str(libs) if libs else None,
            "library_count": len(list(libs.glob("*.prx"))) if libs else 0,
            "commit": version,
            "platform": platform_name(),
            "intel_host": host_is_intel(),
        }


def make_directory_link(target, link):
    target = Path(target)
    link = Path(link)
    if link.is_symlink() or (WINDOWS and link.exists() and _is_junction(link)):
        try:
            if Path(os.path.realpath(link)) == Path(os.path.realpath(target)):
                return
        except OSError:
            pass
        _remove_link(link)
    elif link.exists():
        raise RuntimeError(f"{link} exists and is not a link; remove it to let the launcher manage it")
    link.parent.mkdir(parents=True, exist_ok=True)
    if WINDOWS:
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(str(target), str(link), target_is_directory=True)


def _is_junction(path):
    try:
        return os.path.isjunction(path)
    except AttributeError:
        return False


def _remove_link(link):
    if WINDOWS and link.is_dir() and not link.is_symlink():
        os.rmdir(link)
    else:
        os.unlink(link)


def file_stamp(path):
    try:
        stat = Path(path).stat()
    except OSError:
        return None
    return [stat.st_size, int(stat.st_mtime)]


class Library:
    def __init__(self, home=None):
        self.home = Path(home) if home else default_home()
        self.path = self.home / "library.json"
        self.lock = threading.RLock()
        self.data = {"games": [], "settings": {}}
        self.load()

    def load(self):
        with self.lock:
            if self.path.is_file():
                try:
                    loaded = json.loads(self.path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    loaded = None
                if isinstance(loaded, dict) and isinstance(loaded.get("games"), list):
                    self.data = {"games": loaded["games"], "settings": loaded.get("settings") or {}}

    def save(self):
        with self.lock:
            self.home.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
            os.replace(temporary, self.path)

    @property
    def settings(self):
        return self.data["settings"]

    def games(self):
        with self.lock:
            return list(self.data["games"])

    def get(self, game_id):
        with self.lock:
            for game in self.data["games"]:
                if game["id"] == game_id:
                    return game
        raise KeyError(game_id)

    def find_folder(self, folder):
        folder = str(Path(folder).resolve())
        with self.lock:
            for game in self.data["games"]:
                if game["folder"] == folder:
                    return game
        return None

    def add(self, folder):
        info = scan_game(folder)
        with self.lock:
            existing = self.find_folder(info["folder"])
            if existing is not None:
                existing.update({key: info[key] for key in ("executable", "modules", "icon", "title_id", "version", "problems")})
                self.save()
                return existing
            game = {
                "id": uuid.uuid4().hex[:12],
                "added": time.time(),
                "played": None,
                "intel": "auto",
                "gpu": "",
                "input_config": "",
                **info,
            }
            self.data["games"].append(game)
            self.save()
            return game

    def update(self, game_id, **fields):
        with self.lock:
            game = self.get(game_id)
            for key, value in fields.items():
                if key == "intel" and value not in INTEL_CHOICES:
                    raise ValueError(f"intel must be one of {', '.join(INTEL_CHOICES)}")
                if key in ("title", "intel", "gpu", "input_config", "played"):
                    game[key] = value
            self.save()
            return game

    def remove(self, game_id):
        with self.lock:
            game = self.get(game_id)
            self.data["games"] = [entry for entry in self.data["games"] if entry["id"] != game_id]
            self.save()
            return game

    def update_settings(self, **fields):
        with self.lock:
            for key, value in fields.items():
                if key in ("relinker", "libs", "intel", "gpu"):
                    if value:
                        self.settings[key] = value
                    else:
                        self.settings.pop(key, None)
            self.save()
            return dict(self.settings)


class GameProcess:
    def __init__(self, game_id, process, on_line, on_exit):
        self.game_id = game_id
        self.process = process
        self.started = time.time()
        self.returncode = None
        self.thread = threading.Thread(target=self._pump, args=(on_line, on_exit), daemon=True)
        self.thread.start()

    def _pump(self, on_line, on_exit):
        stream = self.process.stdout
        if stream is not None:
            for raw in iter(stream.readline, b""):
                on_line(raw.decode("utf-8", errors="replace").rstrip("\r\n"))
            stream.close()
        self.returncode = self.process.wait()
        on_exit(self.game_id, self.returncode)

    def running(self):
        return self.process.poll() is None

    def stop(self, grace=3.0):
        if not self.running():
            return
        self.process.terminate()
        deadline = time.time() + grace
        while self.running() and time.time() < deadline:
            time.sleep(0.05)
        if self.running():
            self.process.kill()


class Runtime:
    def __init__(self, library, tooling=None, on_line=None, on_exit=None):
        self.library = library
        self.tooling = tooling or Tooling(library.settings)
        self.on_line = on_line or (lambda game_id, line: None)
        self.on_exit = on_exit or (lambda game_id, code: None)
        self.processes = {}
        self.lock = threading.Lock()

    def game_dir(self, game):
        return self.library.home / "games" / game["id"]

    def output(self, game):
        return self.game_dir(game) / OUTPUT_NAME

    def marker(self, game):
        return self.game_dir(game) / "convert.json"

    def log_path(self, game):
        return self.game_dir(game) / "game.log"

    def use_intel(self, game):
        choice = game.get("intel") or "auto"
        if choice == "auto":
            choice = self.library.settings.get("intel") or "auto"
        if choice == "auto":
            return host_is_intel()
        return choice == "on"

    def convert_options(self, game):
        options = []
        if WINDOWS:
            options.append("--windows")
        if self.use_intel(game):
            options.append("--to-intel")
        return options

    def convert_signature(self, game):
        relinker = self.tooling.relinker()
        return {
            "relinker": file_stamp(relinker) if relinker else None,
            "executable": file_stamp(Path(game["folder"]) / game["executable"]),
            "options": self.convert_options(game),
        }

    def converted(self, game):
        if not self.output(game).is_file():
            return False
        try:
            recorded = json.loads(self.marker(game).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return recorded == self.convert_signature(game)

    def prepare_links(self, game):
        directory = self.game_dir(game)
        directory.mkdir(parents=True, exist_ok=True)
        make_directory_link(game["folder"], directory / "app0")
        libs = self.tooling.libs()
        if libs is None:
            raise RuntimeError("System libraries (libs/*.prx) were not found next to relinker. Build the libs target or choose the folder in Settings")
        make_directory_link(libs, directory / "libs")

    def convert(self, game, log):
        source = Path(game["folder"]) / game["executable"]
        if not source.is_file():
            raise RuntimeError(f"The game executable is gone: {source}")
        directory = self.game_dir(game)
        self.prepare_links(game)
        output = self.output(game)
        marker = self.marker(game)
        if marker.exists():
            marker.unlink()
        command = self.tooling.relinker_command() + self.convert_options(game) + [str(source), str(output)]
        log("$ " + " ".join(command))
        creation = {"creationflags": subprocess.CREATE_NO_WINDOW} if WINDOWS else {}
        with subprocess.Popen(command, cwd=str(directory), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **creation) as process:
            assert process.stdout is not None
            for raw in iter(process.stdout.readline, b""):
                log(raw.decode("utf-8", errors="replace").rstrip("\r\n"))
            code = process.wait()
        if code != 0 or not output.is_file():
            raise RuntimeError(f"relinker failed with exit code {code}; read the log above")
        if not WINDOWS:
            output.chmod(output.stat().st_mode | 0o111)
        marker.write_text(json.dumps(self.convert_signature(game)), encoding="utf-8")
        log(f"Converted {source.name} to {output}")

    def launch_command(self, game):
        return [str(self.output(game))]

    def environment(self, game):
        environment = dict(os.environ)
        gpu = (game.get("gpu") or "").strip() or (self.library.settings.get("gpu") or "").strip()
        if gpu:
            environment["ANYPS5_GPU"] = gpu
        else:
            environment.pop("ANYPS5_GPU", None)
        config = (game.get("input_config") or "").strip()
        if config:
            environment["ANYPS5_INPUT_CONFIG"] = config
        return environment

    def running(self, game_id):
        with self.lock:
            process = self.processes.get(game_id)
        return process is not None and process.running()

    def play(self, game, log):
        if self.running(game["id"]):
            raise RuntimeError("This game is already running")
        if not self.converted(game):
            log("Conversion needed" if self.output(game).is_file() else "First start: converting the executable")
            self.convert(game, log)
        else:
            self.prepare_links(game)
        command = self.launch_command(game)
        log("$ " + " ".join(command))
        creation = {"creationflags": subprocess.CREATE_NO_WINDOW} if WINDOWS else {}
        process = subprocess.Popen(command, cwd=str(self.game_dir(game)), env=self.environment(game), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **creation)
        game_id = game["id"]

        def finished(finished_id, code):
            with self.lock:
                self.processes.pop(finished_id, None)
            self.on_exit(finished_id, code)

        with self.lock:
            self.processes[game_id] = GameProcess(game_id, process, lambda line: self.on_line(game_id, line), finished)
        self.library.update(game_id, played=time.time())
        return process.pid

    def stop(self, game_id):
        with self.lock:
            process = self.processes.get(game_id)
        if process is None:
            return False
        process.stop()
        return True

    def stop_all(self):
        with self.lock:
            processes = list(self.processes.values())
        for process in processes:
            process.stop()

    def forget(self, game):
        self.stop(game["id"])
        directory = self.game_dir(game)
        if not directory.exists():
            return
        for name in ("app0", "libs"):
            link = directory / name
            if link.is_symlink() or (WINDOWS and _is_junction(link)):
                _remove_link(link)
        shutil.rmtree(directory, ignore_errors=True)

    def status(self, game):
        output = self.output(game)
        if self.running(game["id"]):
            return "running"
        if not output.is_file():
            return "new"
        return "ready" if self.converted(game) else "stale"

