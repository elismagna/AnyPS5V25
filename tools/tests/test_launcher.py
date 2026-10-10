import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "launcher"))
import anyps5_launcher as launcher


def make_dump(root, title_id="PPSA00001", title="Sample Title", magic=launcher.ELF_MAGIC, modules="sce_module"):
    (root / "sce_sys").mkdir(parents=True)
    (root / modules).mkdir()
    (root / "sce_sys" / "param.json").write_text(json.dumps({
        "titleId": title_id,
        "contentId": f"UP0000-{title_id}_00-0000000000000000",
        "contentVersion": "01.020.000",
        "localizedParameters": {"defaultLanguage": "en-US", "en-US": {"titleName": title}, "de-DE": {"titleName": "Beispiel"}},
    }), encoding="utf-8")
    (root / "eboot.bin").write_bytes(magic + b"\x00" * 32)
    (root / modules / "libc.prx").write_bytes(launcher.ELF_MAGIC + b"\x00" * 32)
    (root / "data.pak").write_bytes(b"data")
    return root


class ParamTests(unittest.TestCase):
    def test_default_language_title(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = make_dump(Path(directory) / "game")
            parsed = launcher.parse_param(dump / "sce_sys" / "param.json")
            self.assertEqual(parsed["title"], "Sample Title")
            self.assertEqual(parsed["title_id"], "PPSA00001")
            self.assertEqual(parsed["version"], "01.020.000")

    def test_missing_default_language_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "param.json"
            path.write_text(json.dumps({"titleId": "PPSA00002", "localizedParameters": {"ja-JP": {"titleName": "Example"}}}))
            self.assertEqual(launcher.parse_param(path)["title"], "Example")

    def test_malformed_file_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "param.json"
            path.write_text("{not json")
            self.assertEqual(launcher.parse_param(path)["title"], "")


class InspectTests(unittest.TestCase):
    def test_clean_dump_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            info = launcher.inspect_source(make_dump(Path(directory) / "game"))
            self.assertTrue(info["valid"], info["problems"])
            self.assertEqual(info["id"], "PPSA00001")
            self.assertEqual(info["module_dir"], "sce_module")
            self.assertEqual(info["executable_status"], "elf")

    def test_self_container_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            info = launcher.inspect_source(make_dump(Path(directory) / "game", magic=launcher.SELF_MAGIC))
            self.assertFalse(info["valid"])
            self.assertIn("SELF", info["problems"][0])

    def test_missing_modules_and_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = make_dump(Path(directory) / "game")
            (dump / "sce_module" / "libc.prx").unlink()
            (dump / "sce_module").rmdir()
            info = launcher.inspect_source(dump)
            self.assertFalse(info["valid"])
            self.assertTrue(any("sce_module" in problem for problem in info["problems"]))
            self.assertFalse(launcher.inspect_source(Path(directory) / "absent")["valid"])

    def test_both_module_directories_are_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = make_dump(Path(directory) / "game")
            (dump / "sce_modules").mkdir()
            self.assertFalse(launcher.inspect_source(dump)["valid"])

    def test_folder_name_when_param_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = make_dump(Path(directory) / "Homebrew App")
            (dump / "sce_sys" / "param.json").unlink()
            info = launcher.inspect_source(dump)
            self.assertTrue(info["valid"])
            self.assertEqual(info["title"], "Homebrew App")
            self.assertEqual(info["id"], "Homebrew_App")


class CompatibilityTests(unittest.TestCase):
    def test_table_rows(self):
        text = "| Game | ID | Windows | Linux | GPU |\n|---|---|---|---|---|\n| Sample | PPSA00001 | In game, playable | ? | 60 FPS |\n| broken row |\n"
        parsed = launcher.parse_compatibility(text)
        self.assertEqual(parsed["PPSA00001"]["windows"], "In game, playable")
        self.assertEqual(parsed["PPSA00001"]["linux"], "?")
        self.assertEqual(parsed["PPSA00001"]["notes"], ["60 FPS"])
        self.assertEqual(len(parsed), 1)


class CommandTests(unittest.TestCase):
    def make(self, directory, **settings):
        instance = launcher.Launcher(Path(directory) / "config")
        instance.settings.update(settings)
        return instance

    def test_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = self.make(directory, to_intel="off")
            command = instance.conversion_command("relinker", "in.elf", "out.elf", {})
            self.assertEqual(command[0], "relinker")
            self.assertIn("unused-filter=0", command)
            self.assertIn("--registry", command)
            self.assertNotIn("--to-intel", command)
            self.assertEqual(command[-2:], ["in.elf", "out.elf"])
            self.assertTrue(all(isinstance(part, str) for part in command))
            self.assertEqual("--windows" in command, launcher.WINDOWS)

    def test_options_and_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = self.make(directory, to_intel="off", exclude_modules="a.prx, b.prx")
            command = instance.conversion_command("relinker", "in.elf", "out.elf", {"to_intel": "on", "unused_filter": 7, "rpath": "$ORIGIN/x", "skip_syscall_check": True})
            self.assertIn("--to-intel", command)
            self.assertIn("unused-filter=2", command)
            self.assertEqual(command[command.index("--rpath") + 1], "$ORIGIN/x")
            self.assertIn("--skip-syscall-check", command)
            self.assertEqual(command.count("--exclude-sce-module"), 2)
            skipped = instance.conversion_command("relinker", "in.elf", "out.elf", {"skip_sce_module": True})
            self.assertIn("--skip-sce-module", skipped)
            self.assertNotIn("--exclude-sce-module", skipped)

    def test_auto_intel_follows_host(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = self.make(directory, to_intel="auto")
            instance.vendor = "intel"
            self.assertIn("--to-intel", instance.conversion_command("relinker", "a", "b", {}))
            instance.vendor = "amd"
            self.assertNotIn("--to-intel", instance.conversion_command("relinker", "a", "b", {}))

    def test_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = self.make(directory, gpu="RTX", shader_cache=False, require_vulkan=True)
            instance.overrides["PPSA00001"] = {"gpu": "Arc", "extra_env": {"VK_LOADER_DEBUG": "all", "bad name": "x"}}
            env = instance.environment("PPSA00001")
            self.assertEqual(env["ANYPS5_GPU"], "Arc")
            self.assertEqual(env["ANYPS5_NO_SHADER_CACHE"], "1")
            self.assertEqual(env["ANYPS5_REQUIRE_VULKAN"], "1")
            self.assertEqual(env["VK_LOADER_DEBUG"], "all")
            self.assertNotIn("bad name", env)
            self.assertNotIn("ANYPS5_SHADER_CACHE_DIR", instance.environment("other"))


class ScanTests(unittest.TestCase):
    def test_scan_finds_nested_dumps(self):
        with tempfile.TemporaryDirectory() as directory:
            games = Path(directory) / "games"
            make_dump(games / "One", "PPSA00001", "One")
            make_dump(games / "Region" / "Two", "PPSA00002", "Two")
            (games / "Empty").mkdir()
            instance = launcher.Launcher(Path(directory) / "config")
            instance.settings["games_dir"] = str(games)
            instance.scan()
            self.assertEqual(sorted(instance.games), ["PPSA00001", "PPSA00002"])
            state = instance.state()
            self.assertEqual([game["status"] for game in state["games"]], ["ready", "ready"])
            self.assertFalse(state["games"][0]["installed"])


class LinkTests(unittest.TestCase):
    def test_link_and_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "file.txt").write_text("x")
            (root / "dst").mkdir()
            launcher.link_entry(root / "src", root / "dst" / "src", copy=False)
            self.assertEqual((root / "dst" / "src" / "file.txt").read_text(), "x")
            launcher.link_entry(root / "src" / "file.txt", root / "dst" / "file.txt", copy=True)
            self.assertEqual((root / "dst" / "file.txt").read_text(), "x")
            launcher.link_entry(root / "src", root / "dst" / "src", copy=True)
            self.assertFalse((root / "dst" / "src").is_symlink())
            launcher.remove_tree(root / "dst")
            self.assertFalse((root / "dst").exists())
            self.assertTrue((root / "src" / "file.txt").is_file())


class InputConfigTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(launcher.validate_input_config("Cross = KEY:Space\n# note\nR2 = MOUSE:Left\nUp = WHEEL:Up\n"), [])
        errors = launcher.validate_input_config("Nope = KEY:A\nCross KEY:A\nCross = PAD:X\n")
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
