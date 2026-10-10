import json
import os
import sys
import tempfile
import unittest
import unittest.mock
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


class DecryptTests(unittest.TestCase):
    def encrypted_dump(self, root):
        dump = make_dump(root / "games" / "game", magic=launcher.SELF_MAGIC)
        (dump / "sce_module" / "libc.prx").write_bytes(launcher.SELF_MAGIC + b"\x00" * 32)
        return dump

    def test_lists_encrypted_executable_and_modules(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = self.encrypted_dump(Path(directory))
            self.assertEqual(launcher.self_files(dump), ["eboot.bin", "sce_module/libc.prx"])
            info = launcher.inspect_source(dump)
            self.assertFalse(info["valid"])
            self.assertTrue(any("module" in problem and "SELF" in problem for problem in info["problems"]))

    def test_merge_replaces_and_backs_up(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dump = self.encrypted_dump(root)
            usb = root / "usb" / "PS5" / "system_ex" / "app" / "PPSA00001"
            (usb / "sce_module").mkdir(parents=True)
            (usb / "eboot.bin").write_bytes(launcher.ELF_MAGIC + b"\x01" * 32)
            (usb / "sce_module" / "libc.prx").write_bytes(launcher.ELF_MAGIC + b"\x02" * 32)
            other = root / "usb" / "PS5" / "system_ex" / "app" / "PPSA09999"
            other.mkdir(parents=True)
            (other / "eboot.bin").write_bytes(launcher.ELF_MAGIC + b"\x03" * 32)
            result = launcher.merge_decrypted(dump, root / "usb", lambda line: None)
            self.assertEqual(result["missing"], [])
            self.assertEqual((dump / "eboot.bin").read_bytes(), launcher.ELF_MAGIC + b"\x01" * 32)
            self.assertEqual((dump / "_self_backup" / "eboot.bin").read_bytes()[:4], launcher.SELF_MAGIC)
            self.assertTrue(launcher.inspect_source(dump)["valid"])

    def test_ambiguous_match_is_left_alone(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dump = self.encrypted_dump(root)
            for name in ("a", "b"):
                (root / "usb" / name).mkdir(parents=True)
                (root / "usb" / name / "eboot.bin").write_bytes(launcher.ELF_MAGIC + b"\x00" * 8)
            result = launcher.merge_decrypted(dump, root / "usb", lambda line: None)
            self.assertIn("eboot.bin", result["missing"])
            self.assertEqual((dump / "eboot.bin").read_bytes()[:4], launcher.SELF_MAGIC)

    def test_encrypted_candidates_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dump = self.encrypted_dump(root)
            (root / "usb").mkdir()
            (root / "usb" / "eboot.bin").write_bytes(launcher.SELF_MAGIC + b"\x00" * 8)
            self.assertIn("eboot.bin", launcher.merge_decrypted(dump, root / "usb", lambda line: None)["missing"])


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


class PackageTests(unittest.TestCase):
    def test_release_assets_prefers_package_then_release_layout(self):
        tag = "v1.2"
        releases = [
            {"tag_name": "v9", "draft": True, "assets": [{"name": f"AnyPS5-{launcher.PLATFORM}.zip", "browser_download_url": "draft"}]},
            {"tag_name": tag, "assets": [
                {"name": f"relinker-{tag}.exe" if launcher.WINDOWS else f"relinker-{tag}", "browser_download_url": "exe"},
                {"name": f"prx-{launcher.PLATFORM}-{tag}.zip", "browser_download_url": "prx"}]},
            {"tag_name": "latest", "assets": [{"name": f"AnyPS5-{launcher.PLATFORM}.zip", "browser_download_url": "pkg"}]},
        ]
        with unittest.mock.patch.object(launcher, "github_json", return_value=releases):
            self.assertEqual(launcher.release_assets("owner/repo"), (tag, {"relinker": "exe", "libs": "prx"}))
        with unittest.mock.patch.object(launcher, "github_json", return_value=releases[2:]):
            self.assertEqual(launcher.release_assets("owner/repo"), ("latest", {"package": "pkg"}))
        with unittest.mock.patch.object(launcher, "github_json", return_value=[]):
            self.assertEqual(launcher.release_assets("owner/repo"), ("", {}))

    def test_workflow_artifact(self):
        responses = [
            {"workflow_runs": [{"html_url": "run", "head_sha": "abc", "artifacts_url": "artifacts"}]},
            {"artifacts": [{"name": "other", "archive_download_url": "x"}, {"name": f"AnyPS5-{launcher.PLATFORM}", "archive_download_url": "zip", "updated_at": "now", "expired": False}]},
        ]
        with unittest.mock.patch.object(launcher, "github_json", side_effect=responses):
            self.assertEqual(launcher.workflow_artifact("owner/repo"), {"url": "zip", "run": "run", "commit": "abc", "updated": "now"})
        with unittest.mock.patch.object(launcher, "github_json", return_value={"workflow_runs": []}):
            self.assertEqual(launcher.workflow_artifact("owner/repo"), {})

    def test_extract_package_strips_single_root_and_rejects_escapes(self):
        import zipfile
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "pkg.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr(f"AnyPS5-{launcher.PLATFORM}/{launcher.RELINKER}", "bin")
                bundle.writestr(f"AnyPS5-{launcher.PLATFORM}/libs/libc.prx", "prx")
                bundle.writestr(f"AnyPS5-{launcher.PLATFORM}/../escape.txt", "no")
            destination = Path(directory) / "out"
            lines = []
            launcher.extract_package(archive, destination, lines.append)
            self.assertTrue((destination / launcher.RELINKER).is_file())
            self.assertTrue((destination / "libs" / "libc.prx").is_file())
            self.assertFalse((Path(directory) / "escape.txt").exists())
            flat = Path(directory) / "flat.zip"
            with zipfile.ZipFile(flat, "w") as bundle:
                bundle.writestr(launcher.RELINKER, "bin")
                bundle.writestr("COMMIT.txt", "abc")
            launcher.extract_package(flat, Path(directory) / "flat", lines.append)
            self.assertEqual((Path(directory) / "flat" / "COMMIT.txt").read_text(), "abc")


class FakeFtp:
    def __init__(self, listing):
        self.listing = listing

    def mlsd(self, path):
        raise launcher.ftplib.error_perm("500 no MLSD")

    def retrlines(self, command, callback):
        for line in self.listing:
            callback(line)


class FtpTests(unittest.TestCase):
    def test_list_falls_back_to_list_parsing(self):
        lines = [
            "drwxr-xr-x   3 root  root      4096 Jan  1 00:00 sce_sys",
            "-rw-r--r--   1 root  root  12345678 Jan  1 00:00 eboot.bin",
            "drwxr-xr-x   2 root  root      4096 Jan  1 00:00 .",
            "drwxr-xr-x   2 root  root      4096 Jan  1 00:00 sce_module",
        ]
        entries = launcher.ftp_list(FakeFtp(lines), "/dumps/Game")
        self.assertEqual([entry["name"] for entry in entries], ["sce_module", "sce_sys", "eboot.bin"])
        self.assertEqual(entries[2]["size"], 12345678)
        self.assertFalse(entries[2]["dir"])

    def test_connect_requires_host(self):
        with self.assertRaises(RuntimeError):
            launcher.ftp_connect({"ps5_host": ""})


class InputConfigTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(launcher.validate_input_config("Cross = KEY:Space\n# note\nR2 = MOUSE:Left\nUp = WHEEL:Up\n"), [])
        errors = launcher.validate_input_config("Nope = KEY:A\nCross KEY:A\nCross = PAD:X\n")
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
