import json
import os
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "launcher"))
import launcher_core

ELF = b"\x7fELF" + b"\0" * 60

FAKE_RELINKER = textwrap.dedent(
    """
    import json, os, sys
    args = sys.argv[1:]
    options = [a for a in args if a.startswith("--")]
    source, output = [a for a in args if not a.startswith("--")]
    root = os.path.dirname(os.path.abspath(source))
    modules = os.path.join(os.path.dirname(output), "app0", "sce_module")
    os.makedirs(modules, exist_ok=True)
    for name in sorted(os.listdir(os.path.join(root, "sce_module"))):
        if name.endswith(".guest.prx"):
            continue
        with open(os.path.join(modules, name + ".guest.prx"), "wb") as stream:
            stream.write(b"guest")
        print("Guest module: " + os.path.join(modules, name + ".guest.prx"))
    with open(output, "w") as stream:
        stream.write(json.dumps({"options": options, "source": source}))
    print("Output file: " + output)
    """
)

FAKE_GAME = textwrap.dedent(
    """
    import os, sys, time
    print("Physical device candidate: Fake GPU", flush=True)
    print("GPU=" + os.environ.get("ANYPS5_GPU", "") + " CONFIG=" + os.environ.get("ANYPS5_INPUT_CONFIG", ""), flush=True)
    print("cwd=" + os.getcwd(), flush=True)
    if "--linger" in sys.argv:
        time.sleep(30)
    sys.exit(7)
    """
)


def make_dump(root, title="Dreaming Sarah", modules=("libc.prx", "libSceFios2.prx")):
    root.mkdir(parents=True, exist_ok=True)
    (root / "eboot.bin").write_bytes(ELF)
    (root / "sce_module").mkdir(exist_ok=True)
    for name in modules:
        (root / "sce_module" / name).write_bytes(ELF)
    (root / "sce_sys").mkdir(exist_ok=True)
    (root / "sce_sys" / "param.json").write_text(json.dumps({
        "titleId": "PPSA01234",
        "masterVersion": "01.02",
        "localizedParameters": {"defaultLanguage": "de-DE", "de-DE": {"titleName": title}, "en-US": {"titleName": title + " EN"}},
    }), encoding="utf-8")
    (root / "sce_sys" / "icon0.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "level1.pak").write_bytes(b"pak")
    return root


class LauncherTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.dump = make_dump(self.base / "dumps" / "Sarah")
        self.libs = self.base / "package" / "libs"
        self.libs.mkdir(parents=True)
        (self.libs / "libkernel.prx").write_bytes(b"prx")
        self.relinker = self.base / "package" / launcher_core.Tooling({}).relinker_name()
        self.relinker.write_bytes(b"not run directly")
        self.fake_relinker = self.base / "fake_relinker.py"
        self.fake_relinker.write_text(FAKE_RELINKER, encoding="utf-8")
        self.fake_game = self.base / "fake_game.py"
        self.fake_game.write_text(FAKE_GAME, encoding="utf-8")
        self.library = launcher_core.Library(self.home)
        self.library.update_settings(relinker=str(self.relinker), libs=str(self.libs))
        self.lines = []
        self.exits = []
        self.runtime = launcher_core.Runtime(
            self.library,
            on_line=lambda game_id, line: self.lines.append((game_id, line)),
            on_exit=lambda game_id, code: self.exits.append((game_id, code)),
        )
        self.runtime.tooling.relinker_command = lambda: [sys.executable, str(self.fake_relinker)]
        self.runtime.launch_command = lambda game: [sys.executable, str(self.fake_game)] + (["--linger"] if game.get("linger") else [])

    def tearDown(self):
        self.runtime.stop_all()
        self.temp.cleanup()

    def test_scan_reads_title_executable_and_modules(self):
        info = launcher_core.scan_game(self.dump)
        self.assertEqual(info["title"], "Dreaming Sarah")
        self.assertEqual(info["title_id"], "PPSA01234")
        self.assertEqual(info["version"], "01.02")
        self.assertEqual(info["executable"], "eboot.bin")
        self.assertEqual(info["modules"], ["sce_module"])
        self.assertEqual(Path(info["icon"]).name, "icon0.png")
        self.assertEqual(info["problems"], [])

    def test_scan_descends_into_the_folder_that_holds_the_executable(self):
        info = launcher_core.scan_game(self.base / "dumps")
        self.assertEqual(Path(info["folder"]), self.dump.resolve())

    def test_scan_reports_missing_modules_and_missing_executable(self):
        bare = self.base / "bare"
        bare.mkdir()
        (bare / "eboot.bin").write_bytes(ELF)
        info = launcher_core.scan_game(bare)
        self.assertEqual(info["title"], "bare")
        self.assertTrue(any("sce_module" in problem for problem in info["problems"]))
        (self.base / "empty").mkdir()
        with self.assertRaises(ValueError):
            launcher_core.scan_game(self.base / "empty")

    def test_library_persists_games_and_settings(self):
        game = self.library.add(self.dump)
        again = self.library.add(self.dump)
        self.assertEqual(game["id"], again["id"])
        self.library.update(game["id"], intel="on", gpu="NVIDIA", title="Sarah")
        with self.assertRaises(ValueError):
            self.library.update(game["id"], intel="maybe")
        reloaded = launcher_core.Library(self.home)
        self.assertEqual([g["title"] for g in reloaded.games()], ["Sarah"])
        self.assertEqual(reloaded.get(game["id"])["intel"], "on")
        self.assertEqual(reloaded.settings["relinker"], str(self.relinker))
        reloaded.remove(game["id"])
        self.assertEqual(reloaded.games(), [])
        self.assertEqual(launcher_core.Library(self.home).games(), [])

    def test_tooling_finds_relinker_and_libraries_from_settings(self):
        status = self.runtime.tooling.status()
        self.assertEqual(status["relinker"], str(self.relinker.resolve()))
        self.assertEqual(status["libs"], str(self.libs.resolve()))
        self.assertEqual(status["library_count"], 1)
        empty = launcher_core.Tooling({"relinker": str(self.base / "missing")})
        self.assertIsNone(empty.relinker())
        with self.assertRaises(RuntimeError):
            empty.relinker_command()

    def test_intel_detection_follows_the_vendor_string(self):
        self.assertTrue(launcher_core.host_is_intel("Intel64 Family 6, GenuineIntel"))
        self.assertFalse(launcher_core.host_is_intel("AMD64 Family 25, AuthenticAMD"))
        game = self.library.add(self.dump)
        self.library.update(game["id"], intel="on")
        self.assertIn("--to-intel", self.runtime.convert_options(self.library.get(game["id"])))
        self.library.update(game["id"], intel="off")
        self.assertNotIn("--to-intel", self.runtime.convert_options(self.library.get(game["id"])))

    def test_play_converts_links_and_captures_the_game_output(self):
        game = self.library.add(self.dump)
        self.library.update(game["id"], gpu="Fake", input_config="C:/keys.ini")
        game = self.library.get(game["id"])
        self.assertEqual(self.runtime.status(game), "new")
        log = []
        self.runtime.play(game, log.append)
        for _ in range(200):
            if self.exits:
                break
            time.sleep(0.05)
        self.assertEqual(self.exits, [(game["id"], 7)])
        directory = self.runtime.game_dir(game)
        self.assertTrue(self.runtime.output(game).is_file())
        self.assertEqual(Path(os.path.realpath(directory / "app0")), self.dump.resolve())
        self.assertEqual(Path(os.path.realpath(directory / "libs")), self.libs.resolve())
        self.assertTrue((self.dump / "sce_module" / "libc.prx.guest.prx").is_file())
        self.assertTrue(any("Guest module:" in line for line in log))
        self.assertTrue(any(line.startswith("$ ") for line in log))
        texts = [line for _, line in self.lines]
        self.assertIn("GPU=Fake CONFIG=C:/keys.ini", texts)
        self.assertIn("cwd=" + str(directory), [line.replace(os.path.realpath(str(directory)), str(directory)) for line in texts])
        self.assertEqual(self.runtime.status(game), "ready")
        self.assertIsNotNone(self.library.get(game["id"])["played"])
        recorded = json.loads(self.runtime.output(game).read_text())
        self.assertEqual(recorded["options"], self.runtime.convert_options(game))

    def test_changed_executable_or_options_trigger_a_new_conversion(self):
        game = self.library.add(self.dump)
        log = []
        self.runtime.convert(game, log.append)
        self.assertTrue(self.runtime.converted(game))
        self.library.update(game["id"], intel="on" if "--to-intel" not in self.runtime.convert_options(game) else "off")
        self.assertFalse(self.runtime.converted(self.library.get(game["id"])))
        self.runtime.convert(self.library.get(game["id"]), log.append)
        self.assertTrue(self.runtime.converted(self.library.get(game["id"])))
        (self.dump / "eboot.bin").write_bytes(ELF + b"patched")
        future = time.time() + 120
        os.utime(self.dump / "eboot.bin", (future, future))
        self.assertEqual(self.runtime.status(self.library.get(game["id"])), "stale")

    def test_stop_ends_a_running_game_and_forget_removes_its_folder(self):
        game = self.library.add(self.dump)
        game["linger"] = True
        self.runtime.play(game, lambda line: None)
        self.assertTrue(self.runtime.running(game["id"]))
        self.assertEqual(self.runtime.status(game), "running")
        with self.assertRaises(RuntimeError):
            self.runtime.play(game, lambda line: None)
        self.assertTrue(self.runtime.stop(game["id"]))
        for _ in range(200):
            if self.exits:
                break
            time.sleep(0.05)
        self.assertFalse(self.runtime.running(game["id"]))
        self.assertEqual(len(self.exits), 1)
        self.runtime.forget(game)
        self.assertFalse(self.runtime.game_dir(game).exists())
        self.assertTrue((self.dump / "data" / "level1.pak").is_file())
        self.assertFalse(self.runtime.stop(game["id"]))

    def test_links_are_replaced_when_the_target_moves(self):
        link = self.base / "link"
        first = self.base / "first"
        second = self.base / "second"
        first.mkdir()
        second.mkdir()
        launcher_core.make_directory_link(first, link)
        launcher_core.make_directory_link(first, link)
        self.assertEqual(Path(os.path.realpath(link)), first.resolve())
        launcher_core.make_directory_link(second, link)
        self.assertEqual(Path(os.path.realpath(link)), second.resolve())
        plain = self.base / "plain"
        plain.mkdir()
        with self.assertRaises(RuntimeError):
            launcher_core.make_directory_link(first, plain)


if __name__ == "__main__":
    unittest.main()
