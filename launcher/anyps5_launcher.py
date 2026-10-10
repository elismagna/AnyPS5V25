#!/usr/bin/env python3
import argparse
import ftplib
import json
import mimetypes
import os
import platform
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.request
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

LAUNCHER = Path(__file__).resolve().parent
PACKAGE = LAUNCHER.parent
WINDOWS = os.name == "nt"
PLATFORM = "windows" if WINDOWS else "linux"
RELINKER = "relinker.exe" if WINDOWS else "relinker"
OUTPUT = "app.exe" if WINDOWS else "app.elf"
MODULE_DIRS = ("sce_module", "sce_modules", "prx")
EXECUTABLES = ("eboot.bin", "eboot.elf", "eboot.self", "app.elf", "main.elf")
GITHUB_API = "https://api.github.com"
DEFAULT_REPOSITORY = "elismagna/AnyPS5V25"
UPSTREAM_REPOSITORY = "boykopovar/AnyPS5"
ELF_MAGIC = b"\x7fELF"
SELF_MAGIC = b"\x4f\x15\x3d\x1d"
CONTENT_TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png", ".json": "application/json; charset=utf-8", ".md": "text/plain; charset=utf-8"}
ENVIRONMENT = ("ANYPS5_GPU", "ANYPS5_SYSTEM_FONTS", "ANYPS5_SHADER_CACHE_DIR", "ANYPS5_NO_SHADER_CACHE",
               "ANYPS5_ENTITLEMENTS", "ANYPS5_INPUT_CONFIG", "ANYPS5_REQUIRE_VULKAN", "ANYPS5_REQUIRE_DISPLAY")
INPUT_ACTIONS = ("Cross", "Circle", "Triangle", "Square", "L1", "R1", "L2", "R2", "L3", "R3", "Options", "Up", "Right",
                 "Down", "Left", "LeftStickLeft", "LeftStickRight", "LeftStickUp", "LeftStickDown", "RightStickLeft",
                 "RightStickRight", "RightStickUp", "RightStickDown", "TouchLeft", "TouchRight", "ToggleMouse",
                 "ToggleFullscreen")
DEFAULT_SETTINGS = {
    "games_dir": "",
    "install_dir": "",
    "relinker": "",
    "libs": "",
    "fonts": "",
    "to_intel": "auto",
    "unused_filter": 0,
    "windows_gui": True,
    "windows_diagnostics": False,
    "copy_resources": False,
    "rpath": "",
    "gpu": "",
    "shader_cache": True,
    "shader_cache_dir": "",
    "entitlements": "",
    "require_vulkan": False,
    "require_display": False,
    "timing_log_hint": False,
    "skip_sce_module": False,
    "skip_syscall_check": False,
    "lazy_binding": False,
    "exclude_modules": "",
    "ui_sounds": True,
    "clock_24h": False,
    "profile_name": "Player",
    "theme": "ps5",
    "release_repo": DEFAULT_REPOSITORY,
    "github_token": "",
    "ps5_host": "",
    "ps5_port": 2121,
    "ps5_user": "anonymous",
    "ps5_password": "",
    "ps5_path": "/",
    "ps5_payload_port": 9021,
}


def config_dir():
    if WINDOWS:
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / "AnyPS5"
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "anyps5"


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def host_cpu_vendor():
    text = ""
    if WINDOWS:
        text = os.environ.get("PROCESSOR_IDENTIFIER", "") + " " + platform.processor()
    else:
        try:
            text = Path("/proc/cpuinfo").read_text(errors="replace")
        except OSError:
            text = platform.processor()
    if "GenuineIntel" in text or "Intel" in text:
        return "intel"
    if "AuthenticAMD" in text or "AMD" in text:
        return "amd"
    return "unknown"


def find_first(candidates, predicate):
    for candidate in candidates:
        if candidate and predicate(Path(candidate)):
            return Path(candidate)
    return None


def locate_relinker(settings):
    found = find_first([settings.get("relinker"), PACKAGE / RELINKER, PACKAGE / "build" / "core" / "relinker" / RELINKER,
                        PACKAGE / f"AnyPS5-{PLATFORM}" / RELINKER, shutil.which("relinker")], Path.is_file)
    return found


def locate_libs(settings):
    return find_first([settings.get("libs"), PACKAGE / "libs", PACKAGE / "build" / "core" / "libs" / "libs",
                       PACKAGE / f"AnyPS5-{PLATFORM}" / "libs"], lambda p: p.is_dir() and any(p.glob("*.prx")))


def locate_tool(name):
    return find_first([PACKAGE / "tools" / name, LAUNCHER / "tools" / name], Path.is_file)


def locate_compatibility():
    return find_first([PACKAGE / "docs" / "user" / "COMPATIBILITY.md", PACKAGE / "docs" / "COMPATIBILITY.md"], Path.is_file)


def parse_compatibility(text):
    result = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not re.fullmatch(r"[A-Z]{4}\d{5}", cells[1]):
            continue
        result[cells[1]] = {"title": cells[0], "windows": cells[2], "linux": cells[3], "notes": cells[4:]}
    return result


def executable_status(path):
    try:
        with open(path, "rb") as file:
            magic = file.read(4)
    except OSError:
        return "unreadable"
    if magic == ELF_MAGIC:
        return "elf"
    if magic == SELF_MAGIC:
        return "self"
    return "unknown"


def find_executable(folder):
    for name in EXECUTABLES:
        candidate = folder / name
        if candidate.is_file():
            return candidate
    try:
        files = sorted(item for item in folder.iterdir() if item.is_file())
    except OSError:
        return None
    for item in files:
        if item.suffix.lower() in (".elf", ".bin") and executable_status(item) == "elf":
            return item
    return None


def find_module_dir(folder):
    present = [folder / name for name in MODULE_DIRS if (folder / name).is_dir()]
    return present[0] if present else None


def parse_param(path):
    data = read_json(path, {})
    if not isinstance(data, dict):
        data = {}
    localized = data.get("localizedParameters") if isinstance(data.get("localizedParameters"), dict) else {}
    language = localized.get("defaultLanguage") or data.get("defaultLanguage") or "en-US"
    block = localized.get(language) if isinstance(localized.get(language), dict) else {}
    if not block:
        for value in localized.values():
            if isinstance(value, dict) and value.get("titleName"):
                block = value
                break
    return {
        "title_id": str(data.get("titleId") or ""),
        "title": str(block.get("titleName") or data.get("titleName") or ""),
        "content_id": str(data.get("contentId") or ""),
        "version": str(data.get("contentVersion") or data.get("masterVersion") or ""),
        "category": data.get("applicationCategoryType"),
        "required_firmware": str(data.get("requiredSystemSoftwareVersion") or ""),
    }


def slug(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_") or "game"


def inspect_source(folder):
    folder = Path(folder)
    info = {"source": str(folder), "valid": False, "problems": []}
    if not folder.is_dir():
        info["problems"].append("Folder does not exist")
        return info
    executable = find_executable(folder)
    modules = find_module_dir(folder)
    param = folder / "sce_sys" / "param.json"
    meta = parse_param(param) if param.is_file() else {}
    info.update(meta)
    info["executable"] = str(executable) if executable else ""
    info["executable_status"] = executable_status(executable) if executable else "missing"
    info["module_dir"] = modules.name if modules else ""
    info["has_param"] = param.is_file()
    info["icon"] = str(folder / "sce_sys" / "icon0.png") if (folder / "sce_sys" / "icon0.png").is_file() else ""
    art = find_first([folder / "sce_sys" / "pic0.png", folder / "sce_sys" / "pic1.png"], Path.is_file)
    info["art"] = str(art) if art else ""
    if executable is None:
        info["problems"].append("No executable (eboot.bin or an ELF) in the folder")
    elif info["executable_status"] == "self":
        info["problems"].append("The executable is still a SELF container; the relinker needs a clean (decrypted) ELF")
    elif info["executable_status"] != "elf":
        info["problems"].append("The executable is not an ELF file")
    if modules is None:
        info["problems"].append("No sce_module, sce_modules or prx directory beside the executable")
    if sum((folder / name).is_dir() for name in ("sce_module", "sce_modules")) > 1:
        info["problems"].append("Both sce_module and sce_modules are present; keep one")
    if not meta.get("title"):
        info["title"] = folder.name
    info["id"] = slug(meta.get("title_id") or folder.name)
    info["valid"] = not info["problems"]
    return info


def link_entry(source, target, copy):
    source, target = Path(source), Path(target)
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.is_dir():
        if WINDOWS and is_junction(target):
            target.rmdir()
        else:
            shutil.rmtree(target)
    if copy:
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        return "copied"
    try:
        os.symlink(source, target, target_is_directory=source.is_dir())
        return "symlink"
    except OSError:
        pass
    if source.is_dir():
        if WINDOWS:
            try:
                import _winapi
                _winapi.CreateJunction(str(source), str(target))
                return "junction"
            except OSError:
                pass
        shutil.copytree(source, target)
        return "copied"
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        shutil.copy2(source, target)
        return "copied"


def is_junction(path):
    try:
        return bool(os.lstat(path).st_reparse_tag)
    except (OSError, AttributeError):
        return False


def remove_tree(path):
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return
    for item in list(path.iterdir()) if path.is_dir() and not path.is_symlink() else []:
        if item.is_symlink() or item.is_file() or (WINDOWS and is_junction(item)):
            item.unlink() if not item.is_dir() or item.is_symlink() else item.rmdir()
        else:
            remove_tree(item)
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        path.rmdir()


def open_path(path):
    path = str(path)
    if WINDOWS:
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pick_folder(title):
    try:
        if WINDOWS:
            script = ("Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; "
                      f"$d.Description = '{title}'; $d.ShowNewFolderButton = $true; "
                      "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $d.SelectedPath }")
            output = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", script], capture_output=True, text=True, timeout=600).stdout
            return output.strip()
        if sys.platform == "darwin":
            script = f'POSIX path of (choose folder with prompt "{title}")'
            return subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=600).stdout.strip()
        if shutil.which("zenity"):
            return subprocess.run(["zenity", "--file-selection", "--directory", "--title", title], capture_output=True, text=True, timeout=600).stdout.strip()
        if shutil.which("kdialog"):
            return subprocess.run(["kdialog", "--getexistingdirectory", str(Path.home()), "--title", title], capture_output=True, text=True, timeout=600).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return ""


def github_request(url, token="", accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": "AnyPS5-launcher"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def github_json(url, token=""):
    with urllib.request.urlopen(github_request(url, token), timeout=30) as response:
        return json.load(response)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def download_file(url, target, token="", report=None):
    opener = urllib.request.build_opener(NoRedirect)
    headers = {"Accept": "*/*", "User-Agent": "AnyPS5-launcher"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for _ in range(6):
        try:
            response = opener.open(urllib.request.Request(url, headers=headers), timeout=120)
        except urllib.error.HTTPError as error:
            if error.code in (301, 302, 303, 307, 308) and error.headers.get("Location"):
                url = error.headers["Location"]
                headers.pop("Authorization", None)
                continue
            raise RuntimeError(f"download failed with HTTP {error.code}: {url}") from error
        with response, open(target, "wb") as file:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            last = 0
            while True:
                chunk = response.read(1 << 18)
                if not chunk:
                    break
                file.write(chunk)
                done += len(chunk)
                if report and done - last >= 8 << 20:
                    last = done
                    report(f"  {done >> 20} MiB" + (f" of {total >> 20} MiB" if total else ""))
        return target
    raise RuntimeError("too many redirects")


def release_assets(repository, token=""):
    for release in github_json(f"{GITHUB_API}/repos/{repository}/releases?per_page=10", token):
        if release.get("draft"):
            continue
        names = {asset["name"]: asset["browser_download_url"] for asset in release.get("assets", [])}
        tag = release.get("tag_name", "")
        package = names.get(f"AnyPS5-{PLATFORM}.zip")
        if package:
            return tag, {"package": package}
        executable = names.get(f"relinker-{tag}.exe" if WINDOWS else f"relinker-{tag}")
        libraries = names.get(f"prx-{PLATFORM}-{tag}.zip")
        if executable and libraries:
            return tag, {"relinker": executable, "libs": libraries}
    return "", {}


def workflow_artifact(repository, token=""):
    runs = github_json(f"{GITHUB_API}/repos/{repository}/actions/workflows/package.yml/runs?branch=main&status=success&per_page=1", token).get("workflow_runs", [])
    if not runs:
        return {}
    run = runs[0]
    for artifact in github_json(run["artifacts_url"], token).get("artifacts", []):
        if artifact["name"] == f"AnyPS5-{PLATFORM}" and not artifact.get("expired"):
            return {"url": artifact["archive_download_url"], "run": run["html_url"], "commit": run["head_sha"], "updated": artifact.get("updated_at", "")}
    return {}


def extract_package(archive, destination, report):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        members = [member for member in bundle.infolist() if not member.is_dir()]
        roots = {member.filename.split("/")[0] for member in members}
        strip = roots.pop() + "/" if len(roots) == 1 and not any(member.filename in (RELINKER, "COMMIT.txt") for member in members) else ""
        for member in members:
            name = member.filename[len(strip):] if member.filename.startswith(strip) else member.filename
            if not name or name.startswith("/") or ".." in name.split("/"):
                continue
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(member) as source, open(target, "wb") as file:
                shutil.copyfileobj(source, file)
    report(f"Extracted {len(members)} files into {destination}")
    executable = destination / RELINKER
    if executable.is_file() and not WINDOWS:
        executable.chmod(executable.stat().st_mode | 0o111)


def ftp_connect(settings):
    host = (settings.get("ps5_host") or "").strip()
    if not host:
        raise RuntimeError("Set the console address in Settings > Console first")
    connection = ftplib.FTP()
    connection.connect(host, int(settings.get("ps5_port") or 21), timeout=15)
    connection.login(settings.get("ps5_user") or "anonymous", settings.get("ps5_password") or "")
    connection.encoding = "utf-8"
    return connection


def ftp_list(connection, path):
    entries = []
    try:
        for name, facts in connection.mlsd(path):
            if name in (".", ".."):
                continue
            entries.append({"name": name, "dir": facts.get("type") == "dir", "size": int(facts.get("size") or 0)})
        return sorted(entries, key=lambda entry: (not entry["dir"], entry["name"].lower()))
    except (ftplib.error_perm, ftplib.error_proto, ValueError):
        pass
    lines = []
    connection.retrlines(f"LIST {path}", lines.append)
    for line in lines:
        parts = line.split(None, 8)
        if len(parts) < 9 or parts[8] in (".", ".."):
            continue
        size = int(parts[4]) if parts[4].isdigit() else 0
        entries.append({"name": parts[8], "dir": line.startswith("d"), "size": size})
    return sorted(entries, key=lambda entry: (not entry["dir"], entry["name"].lower()))


def ftp_download_tree(connection, remote, local, report, stats):
    local.mkdir(parents=True, exist_ok=True)
    for entry in ftp_list(connection, remote):
        source = remote.rstrip("/") + "/" + entry["name"]
        target = local / entry["name"]
        if entry["dir"]:
            ftp_download_tree(connection, source, target, report, stats)
            continue
        with open(target, "wb") as file:
            connection.retrbinary(f"RETR {source}", file.write, blocksize=1 << 20)
        stats["files"] += 1
        stats["bytes"] += target.stat().st_size
        if stats["files"] % 25 == 0 or entry["size"] > (32 << 20):
            report(f"  {stats['files']} files, {stats['bytes'] >> 20} MiB: {source}")


def relative_time(stamp):
    if not stamp:
        return ""
    delta = int(time.time() - stamp)
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{delta // 60} min ago"
    if delta < 86400:
        return f"{delta // 3600} h ago"
    return f"{delta // 86400} d ago"


class Launcher:
    def __init__(self, config):
        self.config = config
        self.lock = threading.Lock()
        self.settings = {**DEFAULT_SETTINGS, **read_json(config / "launcher.json", {})}
        if not self.settings["games_dir"]:
            self.settings["games_dir"] = str(Path.home() / "AnyPS5" / "Games")
        if not self.settings["install_dir"]:
            self.settings["install_dir"] = str(Path.home() / "AnyPS5" / "Installed")
        self.stats = read_json(config / "stats.json", {})
        self.overrides = read_json(config / "games.json", {})
        self.games = {}
        self.jobs = {}
        self.running = None
        self.notifications = []
        self.token = secrets.token_hex(16)
        self.connected = False
        self.vendor = host_cpu_vendor()
        self.scan()

    def package_commit(self, relinker):
        stamp = find_first([PACKAGE / "COMMIT.txt", relinker.parent / "COMMIT.txt" if relinker else None], Path.is_file)
        return stamp.read_text(encoding="utf-8", errors="replace").strip() if stamp else ""

    def public_settings(self):
        return {**self.settings, "github_token": "set" if self.settings.get("github_token") else ""}

    def save(self):
        write_json(self.config / "launcher.json", self.settings)
        write_json(self.config / "stats.json", self.stats)
        write_json(self.config / "games.json", self.overrides)

    def notify(self, title, text=""):
        with self.lock:
            self.notifications.append({"id": secrets.token_hex(4), "title": title, "text": text, "time": time.time()})
            self.notifications = self.notifications[-30:]

    def install_root(self, game_id):
        return Path(self.settings["install_dir"]) / game_id

    def scan(self):
        games = {}
        root = Path(self.settings["games_dir"])
        folders = []
        if root.is_dir():
            for entry in sorted(root.iterdir()):
                if entry.is_dir():
                    folders.append(entry)
                    for nested in sorted(entry.iterdir()):
                        if nested.is_dir() and (nested / "sce_sys").is_dir():
                            folders.append(nested)
        for folder in folders:
            if not ((folder / "sce_sys").is_dir() or find_executable(folder)):
                continue
            info = inspect_source(folder)
            if not info.get("executable") and not info.get("has_param"):
                continue
            games[info["id"]] = info
        install = Path(self.settings["install_dir"])
        if install.is_dir():
            for entry in sorted(install.iterdir()):
                if entry.is_dir() and entry.name not in games and (entry / "install.json").is_file():
                    record = read_json(entry / "install.json", {})
                    source = record.get("source", "")
                    info = inspect_source(source) if source and Path(source).is_dir() else {"id": entry.name, "title": record.get("title") or entry.name, "title_id": record.get("title_id", ""), "source": source, "valid": False, "problems": ["Source folder is missing"], "icon": "", "art": ""}
                    info["id"] = entry.name
                    games[entry.name] = info
        with self.lock:
            self.games = games

    def game_view(self, info, compatibility):
        game_id = info["id"]
        run = self.install_root(game_id)
        record = read_json(run / "install.json", {})
        stats = self.stats.get(game_id, {})
        compat = compatibility.get(info.get("title_id", ""), {})
        audit = read_json(run / "audit.json", {}) if (run / "audit.json").is_file() else {}
        installed = (run / OUTPUT).is_file()
        status = "installed" if installed else ("blocked" if not info.get("valid") else "ready")
        if self.running and self.running["id"] == game_id:
            status = "running"
        return {
            **info,
            "installed": installed,
            "status": status,
            "run_dir": str(run),
            "install": record,
            "compatibility": compat.get(PLATFORM, ""),
            "compatibility_notes": compat,
            "audit": {key: audit.get(key) for key in ("unique_by_class", "total", "missing_libraries", "source_commit")} if audit else None,
            "last_played": stats.get("last_played", 0),
            "last_played_text": relative_time(stats.get("last_played", 0)),
            "play_seconds": stats.get("play_seconds", 0),
            "last_exit": stats.get("last_exit"),
            "last_error": stats.get("last_error", ""),
            "launches": stats.get("launches", 0),
            "overrides": self.overrides.get(game_id, {}),
            "has_save": (run / "_sd").is_dir(),
            "has_input": (run / "anyps5-input.ini").is_file(),
            "has_log": (run / "anyps5-launcher.log").is_file(),
        }

    def state(self):
        compatibility_file = locate_compatibility()
        compatibility = parse_compatibility(compatibility_file.read_text(encoding="utf-8", errors="replace")) if compatibility_file else {}
        relinker = locate_relinker(self.settings)
        libs = locate_libs(self.settings)
        with self.lock:
            games = [self.game_view(info, compatibility) for info in self.games.values()]
            running = dict(self.running, process=None) if self.running else None
            notifications = list(self.notifications)
        games.sort(key=lambda game: (-game["last_played"], game["title"].lower()))
        return {
            "settings": self.public_settings(),
            "games": games,
            "running": running and {key: value for key, value in running.items() if key != "process"},
            "notifications": notifications,
            "host": {
                "platform": PLATFORM,
                "os": platform.platform(),
                "cpu": platform.processor() or platform.machine(),
                "cpu_vendor": self.vendor,
                "relinker": str(relinker) if relinker else "",
                "libs": str(libs) if libs else "",
                "libs_count": len(list(libs.glob("*.prx"))) if libs else 0,
                "audit_tool": bool(locate_tool("import_audit.py")),
                "compatibility_list": str(compatibility_file) if compatibility_file else "",
                "compatibility": compatibility,
                "python": platform.python_version(),
                "config": str(self.config),
                "package": str(PACKAGE),
                "commit": self.package_commit(relinker),
            },
            "jobs": {job_id: self.job_view(job) for job_id, job in self.jobs.items()},
        }

    def job_view(self, job):
        return {key: value for key, value in job.items() if key != "thread"}

    def start_job(self, kind, game_id, target):
        job = {"id": secrets.token_hex(4), "kind": kind, "game": game_id, "status": "running", "log": [], "started": time.time(), "finished": 0, "result": None, "error": ""}
        job["thread"] = threading.Thread(target=self.run_job, args=(job, target), daemon=True)
        self.jobs[job["id"]] = job
        job["thread"].start()
        return job

    def run_job(self, job, target):
        try:
            job["result"] = target(job)
            job["status"] = "done"
        except Exception as error:
            job["status"] = "failed"
            job["error"] = str(error)
            job["log"].append(f"FAIL: {error}")
        job["finished"] = time.time()

    def stream(self, job, command, cwd=None, env=None):
        job["log"].append("+ " + " ".join(str(part) for part in command))
        process = subprocess.Popen([str(part) for part in command], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", bufsize=1)
        for line in process.stdout:
            job["log"].append(line.rstrip("\n"))
        return process.wait()

    def conversion_command(self, relinker, source, output, options):
        command = [relinker]
        if WINDOWS:
            command.append("--windows")
            if options.get("windows_gui", self.settings["windows_gui"]):
                command.append("--windows-gui")
            if options.get("windows_diagnostics", self.settings["windows_diagnostics"]):
                command.append("--windows-diagnostics")
        to_intel = options.get("to_intel", self.settings["to_intel"])
        if to_intel is True or to_intel == "on" or (to_intel == "auto" and self.vendor == "intel"):
            command.append("--to-intel")
        unused = int(options.get("unused_filter", self.settings["unused_filter"]) or 0)
        command.append(f"unused-filter={min(max(unused, 0), 2)}")
        command.append("--registry")
        rpath = options.get("rpath", self.settings["rpath"])
        if rpath:
            command += ["--rpath", rpath]
        if options.get("skip_sce_module", self.settings["skip_sce_module"]):
            command.append("--skip-sce-module")
        else:
            for name in re.split(r"[,\s]+", str(options.get("exclude_modules", self.settings["exclude_modules"]) or "")):
                if name:
                    command += ["--exclude-sce-module", name]
        if options.get("skip_syscall_check", self.settings["skip_syscall_check"]):
            command.append("--skip-syscall-check")
        if options.get("lazy_binding", self.settings["lazy_binding"]):
            command.append("--lazy-binding")
        command += [str(source), str(output)]
        return [str(part) for part in command]

    def install(self, source, options):
        info = inspect_source(source)
        if not info["valid"]:
            raise RuntimeError("; ".join(info["problems"]))
        relinker = locate_relinker(self.settings)
        libs = locate_libs(self.settings)
        if relinker is None:
            raise RuntimeError("relinker not found: build the package or set its path in Settings > Paths")
        if libs is None:
            raise RuntimeError("System libraries not found: build the libs target or set their path in Settings > Paths")
        game_id = info["id"]
        run = self.install_root(game_id)

        def work(job):
            run.mkdir(parents=True, exist_ok=True)
            output = run / OUTPUT
            job["log"].append(f"Installing {info['title']} ({info.get('title_id') or game_id}) into {run}")
            code = self.stream(job, self.conversion_command(relinker, info["executable"], output, options))
            if code != 0:
                raise RuntimeError(f"relinker exited with code {code}")
            if not WINDOWS:
                output.chmod(output.stat().st_mode | 0o111)
            copy = bool(options.get("copy_resources", self.settings["copy_resources"]))
            app0 = run / "app0"
            app0.mkdir(exist_ok=True)
            source_dir = Path(info["source"])
            executable = Path(info["executable"])
            module_dir = info["module_dir"]
            for entry in sorted(source_dir.iterdir()):
                if entry == executable or entry.name == module_dir:
                    continue
                how = link_entry(entry, app0 / entry.name, copy)
                job["log"].append(f"app0/{entry.name}: {how}")
            job["log"].append(f"libs: {link_entry(libs, run / 'libs', copy)}")
            fonts = self.settings.get("fonts")
            if fonts and Path(fonts).is_dir():
                job["log"].append(f"anyps5-fonts: {link_entry(fonts, run / 'anyps5-fonts', copy)}")
            write_json(run / "install.json", {"source": str(source_dir), "title": info["title"], "title_id": info.get("title_id", ""), "installed": time.time(), "options": options, "command": self.conversion_command(relinker, info["executable"], output, options), "libs": str(libs)})
            self.scan()
            self.notify("Installed", info["title"])
            return {"id": game_id}

        return self.start_job("install", game_id, work)

    def audit(self, game_id):
        run = self.install_root(game_id)
        tool = locate_tool("import_audit.py")
        libs = locate_libs(self.settings)
        if tool is None:
            raise RuntimeError("tools/import_audit.py is not available in this package")
        if libs is None:
            raise RuntimeError("System libraries not found")
        registries = sorted(run.glob("*.registry.json"))
        if not registries:
            raise RuntimeError("No registry files: reinstall the game to generate them")
        info = self.games.get(game_id, {})

        def work(job):
            command = [sys.executable, tool, *registries, "--libs", libs, "--json", run / "audit.json"]
            if (run / "audit.json").is_file():
                (run / "audit.json").unlink()
            if info.get("source") and info.get("module_dir"):
                command += ["--modules", Path(info["source"]) / info["module_dir"]]
            source = PACKAGE / "core" / "libs" / "prx"
            temporary = None
            if source.is_dir():
                command += ["--source", source]
            else:
                temporary = tempfile.mkdtemp(prefix="anyps5-audit-")
                command += ["--source", temporary]
                job["log"].append("Source tree not available: throwing stubs are counted as implemented")
            try:
                code = self.stream(job, command, cwd=tool.parent)
            finally:
                if temporary:
                    shutil.rmtree(temporary, ignore_errors=True)
            if not (run / "audit.json").is_file():
                raise RuntimeError(f"audit did not produce a result (exit code {code})")
            job["log"].append({0: "Nothing blocks loading", 1: "Some imports are absent: the title will not load until they are implemented"}.get(code, f"exit code {code}"))
            return read_json(run / "audit.json", {})

        return self.start_job("audit", game_id, work)

    def environment(self, game_id):
        env = dict(os.environ)
        for name in ENVIRONMENT:
            env.pop(name, None)
        merged = {**self.settings, **self.overrides.get(game_id, {})}
        if merged.get("gpu"):
            env["ANYPS5_GPU"] = merged["gpu"]
        if merged.get("fonts"):
            env["ANYPS5_SYSTEM_FONTS"] = merged["fonts"]
        if not merged.get("shader_cache", True):
            env["ANYPS5_NO_SHADER_CACHE"] = "1"
        elif merged.get("shader_cache_dir"):
            env["ANYPS5_SHADER_CACHE_DIR"] = merged["shader_cache_dir"]
        if merged.get("entitlements"):
            env["ANYPS5_ENTITLEMENTS"] = merged["entitlements"]
        if merged.get("require_vulkan"):
            env["ANYPS5_REQUIRE_VULKAN"] = "1"
        if merged.get("require_display"):
            env["ANYPS5_REQUIRE_DISPLAY"] = "1"
        for name, value in (merged.get("extra_env") or {}).items():
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                env[name] = str(value)
        return env

    def launch(self, game_id):
        if self.running:
            raise RuntimeError("A game is already running; close it first")
        run = self.install_root(game_id)
        executable = run / OUTPUT
        if not executable.is_file():
            raise RuntimeError("Not installed yet")
        log = open(run / "anyps5-launcher.log", "w", encoding="utf-8", errors="replace")
        process = subprocess.Popen([str(executable)], cwd=run, env=self.environment(game_id), stdout=log, stderr=subprocess.STDOUT)
        log.close()
        with self.lock:
            self.running = {"id": game_id, "pid": process.pid, "started": time.time(), "process": process}
        stats = self.stats.setdefault(game_id, {})
        stats["launches"] = stats.get("launches", 0) + 1
        stats["last_played"] = time.time()
        self.save()
        threading.Thread(target=self.watch, args=(game_id, process), daemon=True).start()
        return process.pid

    def watch(self, game_id, process):
        code = process.wait()
        with self.lock:
            started = self.running["started"] if self.running else time.time()
            self.running = None
        stats = self.stats.setdefault(game_id, {})
        stats["play_seconds"] = stats.get("play_seconds", 0) + int(time.time() - started)
        stats["last_exit"] = code
        stats["last_error"] = self.last_error(game_id)
        self.save()
        title = self.games.get(game_id, {}).get("title", game_id)
        self.notify("Game closed" if code == 0 else f"Game stopped (exit code {code})", title if code == 0 else stats["last_error"] or title)

    def last_error(self, game_id):
        try:
            lines = (self.install_root(game_id) / "anyps5-launcher.log").read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return ""
        for line in reversed(lines[-200:]):
            if "terminate called" in line or "what()" in line or line.startswith("FAIL") or "error" in line.lower():
                return line.strip()[:300]
        return ""

    def stop(self):
        with self.lock:
            running = self.running
        if not running:
            return False
        process = running["process"]
        process.terminate()
        for _ in range(30):
            if process.poll() is not None:
                return True
            time.sleep(0.1)
        process.kill()
        return True

    def log(self, game_id, tail=400):
        path = self.install_root(game_id) / "anyps5-launcher.log"
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []
        return lines[-tail:]

    def input_config(self, game_id):
        path = self.install_root(game_id) / "anyps5-input.ini"
        try:
            return {"exists": True, "text": path.read_text(encoding="utf-8", errors="replace")}
        except OSError:
            return {"exists": False, "text": ""}

    def write_input_config(self, game_id, text):
        path = self.install_root(game_id) / "anyps5-input.ini"
        if not path.parent.is_dir():
            raise RuntimeError("Install the game first")
        errors = validate_input_config(text)
        if errors:
            raise RuntimeError("; ".join(errors))
        if text.strip():
            path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        elif path.is_file():
            path.unlink()

    def backup_save(self, game_id):
        run = self.install_root(game_id)
        if not (run / "_sd").is_dir():
            raise RuntimeError("This game has no save data yet")
        backups = self.config / "backups"
        backups.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        archive = shutil.make_archive(str(backups / f"{game_id}-{stamp}"), "zip", run, "_sd")
        self.notify("Save data backed up", Path(archive).name)
        return archive

    def shader_cache_dirs(self):
        result = []
        for info in self.games.values():
            path = self.install_root(info["id"]) / "shader_cache"
            if path.is_dir():
                result.append(path)
        custom = self.settings.get("shader_cache_dir")
        if custom and Path(custom).is_dir():
            result.append(Path(custom))
        return result

    def clear_shader_cache(self):
        count = 0
        for path in self.shader_cache_dirs():
            shutil.rmtree(path, ignore_errors=True)
            count += 1
        self.notify("Shader cache cleared", f"{count} cache folder(s)")
        return count

    def remove(self, game_id):
        if self.running and self.running["id"] == game_id:
            raise RuntimeError("Close the game first")
        run = self.install_root(game_id)
        if run.is_dir():
            remove_tree(run)
        self.stats.pop(game_id, None)
        self.overrides.pop(game_id, None)
        self.save()
        self.scan()
        self.notify("Removed", game_id)

    def setup_relinker(self):
        token = self.settings.get("github_token") or ""
        repositories = []
        for repository in (self.settings.get("release_repo") or DEFAULT_REPOSITORY, DEFAULT_REPOSITORY, UPSTREAM_REPOSITORY):
            if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) and repository not in repositories:
                repositories.append(repository)
        destination = PACKAGE / f"AnyPS5-{PLATFORM}"

        def work(job):
            report = job["log"].append
            downloads = self.config / "downloads"
            downloads.mkdir(parents=True, exist_ok=True)
            for repository in repositories:
                report(f"Looking for a {PLATFORM} package in {repository}")
                try:
                    tag, assets = release_assets(repository, token)
                except (urllib.error.URLError, OSError, ValueError) as error:
                    report(f"  releases: {error}")
                    tag, assets = "", {}
                if assets:
                    report(f"  release {tag}")
                    if "package" in assets:
                        archive = downloads / f"AnyPS5-{PLATFORM}-{tag}.zip"
                        download_file(assets["package"], archive, token, report)
                        extract_package(archive, destination, report)
                    else:
                        destination.mkdir(parents=True, exist_ok=True)
                        download_file(assets["relinker"], destination / RELINKER, token, report)
                        if not WINDOWS:
                            (destination / RELINKER).chmod(0o755)
                        archive = downloads / f"prx-{PLATFORM}-{tag}.zip"
                        download_file(assets["libs"], archive, token, report)
                        extract_package(archive, destination / "libs", report)
                    break
                try:
                    artifact = workflow_artifact(repository, token)
                except (urllib.error.URLError, OSError, ValueError) as error:
                    report(f"  workflow artifacts: {error}")
                    artifact = {}
                if artifact:
                    report(f"  Package workflow run {artifact['run']} (commit {artifact['commit'][:10]}, {artifact['updated']})")
                    archive = downloads / f"AnyPS5-{PLATFORM}-artifact.zip"
                    try:
                        download_file(artifact["url"], archive, token, report)
                    except RuntimeError as error:
                        report(f"  {error}")
                        report("  Artifact downloads can need a GitHub token: create a fine-grained token with Actions read access and paste it in Settings > Paths")
                        continue
                    extract_package(archive, destination, report)
                    (destination / "COMMIT.txt").write_text(artifact["commit"] + "\n", encoding="utf-8")
                    break
                report("  nothing published yet")
            relinker = locate_relinker(self.settings)
            libs = locate_libs(self.settings)
            if relinker is None or libs is None:
                raise RuntimeError("No package could be downloaded. Build it with tools/build_package.py or download the AnyPS5 artifact from the Actions page and extract it into " + str(destination))
            self.settings["relinker"] = ""
            self.settings["libs"] = ""
            self.save()
            report(f"relinker: {relinker}")
            report(f"system libraries: {len(list(libs.glob('*.prx')))} in {libs}")
            self.notify("relinker ready", str(relinker))
            return {"relinker": str(relinker), "libs": str(libs)}

        return self.start_job("setup", "", work)

    def build_package(self):
        script = PACKAGE / "tools" / "build_package.py"
        if not script.is_file():
            raise RuntimeError("tools/build_package.py is not available here; run the setup from a repository checkout")

        def work(job):
            code = self.stream(job, [sys.executable, script], cwd=PACKAGE)
            if code != 0:
                raise RuntimeError(f"build failed with exit code {code}; the toolchain requirements are in docs/dev/BUILD.md")
            self.notify("Build finished", "relinker and system libraries are ready")
            return {"relinker": str(locate_relinker(self.settings) or "")}

        return self.start_job("build", "", work)

    def send_payload(self, path):
        import socket
        payload = Path(path)
        if not payload.is_file():
            raise RuntimeError("Payload file not found")
        if executable_status(payload) != "elf":
            raise RuntimeError("A payload is an ELF file built for the console")
        host = (self.settings.get("ps5_host") or "").strip()
        if not host:
            raise RuntimeError("Set the console address in Settings > Console first")
        data = payload.read_bytes()
        with socket.create_connection((host, int(self.settings.get("ps5_payload_port") or 9021)), timeout=15) as connection:
            connection.sendall(data)
        self.notify("Payload sent", f"{payload.name} ({len(data) >> 10} KiB) to {host}")
        return len(data)

    def console_list(self, path):
        connection = ftp_connect(self.settings)
        try:
            return ftp_list(connection, path or "/")
        finally:
            connection.close()

    def console_import(self, path, install):
        name = slug(path.rstrip("/").split("/")[-1] or "console-dump")
        target = Path(self.settings["games_dir"]) / name

        def work(job):
            report = job["log"].append
            report(f"Connecting to {self.settings['ps5_host']}:{self.settings['ps5_port']}")
            connection = ftp_connect(self.settings)
            stats = {"files": 0, "bytes": 0}
            try:
                report(f"Downloading {path} into {target}")
                ftp_download_tree(connection, path, target, report, stats)
            finally:
                connection.close()
            report(f"Done: {stats['files']} files, {stats['bytes'] >> 20} MiB")
            self.scan()
            info = inspect_source(target)
            if not info["valid"]:
                report("Imported, but it cannot be converted yet: " + "; ".join(info["problems"]))
                self.notify("Imported", info["title"])
                return {"id": info["id"], "installed": False}
            if install:
                inner = self.install(str(target), {})
                inner["thread"].join()
                job["log"].extend(inner["log"])
                if inner["status"] != "done":
                    raise RuntimeError(inner["error"])
            return {"id": info["id"], "installed": bool(install)}

        return self.start_job("import", name, work)

    def gpus(self):
        names = []
        if shutil.which("vulkaninfo"):
            try:
                output = subprocess.run(["vulkaninfo", "--summary"], capture_output=True, text=True, timeout=20, errors="replace").stdout
                names += re.findall(r"deviceName\s*=\s*(.+)", output)
            except (OSError, subprocess.SubprocessError):
                pass
        for info in self.games.values():
            for line in self.log(info["id"], 2000):
                match = re.search(r"Physical device candidate=\S+ name=(.+?) api=", line)
                if match:
                    names.append(match.group(1).strip())
        seen = []
        for name in names:
            if name.strip() and name.strip() not in seen:
                seen.append(name.strip())
        return seen


def validate_input_config(text):
    errors = []
    actions = {action.lower() for action in INPUT_ACTIONS}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].split(";", 1)[0].strip().lstrip("﻿")
        if not line:
            continue
        if "=" not in line:
            errors.append(f"line {number}: expected Action = Type:Value")
            continue
        action, binding = (part.strip() for part in line.split("=", 1))
        if action.lower() not in actions:
            errors.append(f"line {number}: unknown action {action}")
        if not re.fullmatch(r"(KEY:.+|MOUSE:(Left|Middle|Right|X1|X2)|WHEEL:(Up|Down))", binding):
            errors.append(f"line {number}: unknown binding {binding}")
    return errors


class Handler(BaseHTTPRequestHandler):
    launcher = None
    server_version = "AnyPS5Launcher/1.0"

    def log_message(self, format, *args):
        if self.server.verbose:
            super().log_message(format, *args)

    def send_json(self, value, status=200):
        body = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type=None):
        try:
            data = Path(path).read_bytes()
        except OSError:
            self.send_json({"error": "not found"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type or CONTENT_TYPES.get(Path(path).suffix.lower()) or mimetypes.guess_type(str(path))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def authorized(self):
        return self.headers.get("X-AnyPS5-Token") == self.launcher.token or self.query().get("t") == self.launcher.token

    def query(self):
        return {key: values[-1] for key, values in parse_qs(urlparse(self.path).query).items()}

    def do_GET(self):
        route = urlparse(self.path).path
        if route in ("/", "/index.html"):
            if not self.launcher.connected:
                self.launcher.connected = True
                print("Browser connected.", flush=True)
            page = (LAUNCHER / "ui" / "index.html").read_text(encoding="utf-8").replace("__TOKEN__", self.launcher.token)
            data = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        if route.startswith("/ui/"):
            target = (LAUNCHER / "ui" / route[4:]).resolve()
            if target.is_file() and LAUNCHER / "ui" in target.parents:
                self.send_file(target)
            else:
                self.send_json({"error": "not found"}, 404)
            return
        if route.startswith("/api/"):
            if not self.authorized():
                self.send_json({"error": "forbidden"}, 403)
                return
            try:
                self.api_get(route[5:], self.query())
            except Exception as error:
                self.send_json({"error": str(error)}, 400)
            return
        self.send_json({"error": "not found"}, 404)

    def api_get(self, name, query):
        launcher = self.launcher
        if name == "state":
            self.send_json(launcher.state())
        elif name == "job":
            job = launcher.jobs.get(query.get("id", ""))
            if job is None:
                self.send_json({"error": "unknown job"}, 404)
            else:
                self.send_json(launcher.job_view(job))
        elif name == "log":
            self.send_json({"lines": launcher.log(query.get("id", ""))})
        elif name == "audit":
            self.send_json(read_json(launcher.install_root(query.get("id", "")) / "audit.json", {}))
        elif name in ("icon", "art"):
            info = launcher.games.get(query.get("id", ""), {})
            path = info.get(name)
            if path and Path(path).is_file():
                self.send_file(path, "image/png")
            else:
                self.send_json({"error": "no image"}, 404)
        elif name == "input":
            self.send_json({**launcher.input_config(query.get("id", "")), "actions": INPUT_ACTIONS})
        elif name == "gpus":
            self.send_json({"gpus": launcher.gpus()})
        elif name == "inspect":
            self.send_json(inspect_source(query.get("source", "")))
        elif name == "console-list":
            self.send_json({"path": query.get("path", "/"), "entries": launcher.console_list(query.get("path", "/"))})
        elif name == "docs":
            docs = find_first([PACKAGE / "docs" / "user", PACKAGE / "docs"], Path.is_dir)
            files = sorted(docs.glob("*.md")) if docs else []
            self.send_json({"docs": [{"name": file.stem, "text": file.read_text(encoding="utf-8", errors="replace")} for file in files]})
        else:
            self.send_json({"error": "unknown endpoint"}, 404)

    def do_POST(self):
        route = urlparse(self.path).path
        if not route.startswith("/api/") or not self.authorized():
            self.send_json({"error": "forbidden"}, 403)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            self.api_post(route[5:], body if isinstance(body, dict) else {})
        except Exception as error:
            self.send_json({"error": str(error)}, 400)

    def api_post(self, name, body):
        launcher = self.launcher
        if name == "settings":
            for key, value in body.items():
                if key in DEFAULT_SETTINGS and not (key == "github_token" and value == "set"):
                    launcher.settings[key] = value
            launcher.save()
            launcher.scan()
            self.send_json({"ok": True, "settings": launcher.public_settings()})
        elif name == "scan":
            launcher.scan()
            self.send_json({"ok": True, "count": len(launcher.games)})
        elif name == "install":
            job = launcher.install(body.get("source", ""), body.get("options") or {})
            self.send_json({"ok": True, "job": job["id"]})
        elif name == "audit":
            job = launcher.audit(body.get("id", ""))
            self.send_json({"ok": True, "job": job["id"]})
        elif name == "setup-relinker":
            self.send_json({"ok": True, "job": launcher.setup_relinker()["id"]})
        elif name == "build-package":
            self.send_json({"ok": True, "job": launcher.build_package()["id"]})
        elif name == "console-payload":
            self.send_json({"ok": True, "bytes": launcher.send_payload(body.get("path", ""))})
        elif name == "console-import":
            self.send_json({"ok": True, "job": launcher.console_import(body.get("path", "/"), bool(body.get("install", True)))["id"]})
        elif name == "launch":
            self.send_json({"ok": True, "pid": launcher.launch(body.get("id", ""))})
        elif name == "stop":
            self.send_json({"ok": True, "stopped": launcher.stop()})
        elif name == "pick-folder":
            self.send_json({"path": pick_folder(body.get("title") or "Select a folder")})
        elif name == "open":
            target = body.get("path", "")
            game = launcher.games.get(body.get("id", ""))
            what = body.get("what", "")
            if game and what:
                run = launcher.install_root(game["id"])
                target = {"source": game.get("source", ""), "run": str(run), "save": str(run / "_sd"), "config": str(launcher.config)}.get(what, "")
            if not target or not Path(target).exists():
                raise RuntimeError("Folder does not exist")
            open_path(target)
            self.send_json({"ok": True})
        elif name == "input":
            launcher.write_input_config(body.get("id", ""), body.get("text", ""))
            self.send_json({"ok": True})
        elif name == "game-settings":
            game_id = body.get("id", "")
            overrides = body.get("overrides") or {}
            if overrides:
                launcher.overrides[game_id] = overrides
            else:
                launcher.overrides.pop(game_id, None)
            launcher.save()
            self.send_json({"ok": True})
        elif name == "save-backup":
            self.send_json({"ok": True, "archive": launcher.backup_save(body.get("id", ""))})
        elif name == "clear-shader-cache":
            self.send_json({"ok": True, "count": launcher.clear_shader_cache()})
        elif name == "remove":
            launcher.remove(body.get("id", ""))
            self.send_json({"ok": True})
        elif name == "dismiss":
            with launcher.lock:
                launcher.notifications = [item for item in launcher.notifications if item["id"] != body.get("id")]
            self.send_json({"ok": True})
        elif name == "quit":
            self.send_json({"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_json({"error": "unknown endpoint"}, 404)


def find_browser_app_mode():
    names = ["chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "microsoft-edge", "brave", "brave-browser"]
    if WINDOWS:
        roots = [os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""), os.environ.get("LOCALAPPDATA", "")]
        for root in roots:
            for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe", "BraveSoftware/Brave-Browser/Application/brave.exe"):
                candidate = Path(root) / relative if root else None
                if candidate and candidate.is_file():
                    return str(candidate)
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return ""


def open_ui(url, mode):
    if mode == "none":
        return
    if mode in ("app", "auto"):
        browser = find_browser_app_mode()
        if browser:
            flags = [f"--app={url}", "--new-window", "--window-size=1600,900", "--no-first-run", "--no-default-browser-check", "--autoplay-policy=no-user-gesture-required", "--user-data-dir=" + str(config_dir() / "browser")]
            try:
                subprocess.Popen([browser, *flags], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except OSError:
                pass
        if mode == "app":
            print("No Chromium-based browser found for app mode; opening the default browser", flush=True)
    webbrowser.open(url)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            try:
                stream.write(text)
                stream.flush()
            except (OSError, ValueError):
                pass

    def flush(self):
        for stream in self.streams:
            try:
                stream.flush()
            except (OSError, ValueError):
                pass


def main(argv=None):
    parser = argparse.ArgumentParser(description="PS5-style launcher for AnyPS5: install, audit and run converted titles")
    parser.add_argument("--port", type=int, default=7355)
    parser.add_argument("--config", type=Path, default=config_dir())
    parser.add_argument("--browser", choices=("auto", "app", "default", "none"), default="auto", help="auto: borderless app window when a Chromium browser exists, else the default browser")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    args.config.mkdir(parents=True, exist_ok=True)
    log = open(args.config / "launcher.log", "w", encoding="utf-8", errors="replace")
    sys.stdout = Tee(sys.__stdout__, log)
    sys.stderr = Tee(sys.__stderr__, log)
    print(f"AnyPS5 launcher starting: Python {platform.python_version()} on {platform.platform()}; log: {args.config / 'launcher.log'}", flush=True)
    launcher = Launcher(args.config)
    Handler.launcher = launcher
    server = None
    for port in [args.port, 0]:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    server.verbose = args.verbose
    server.daemon_threads = True
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"AnyPS5 launcher: {url}", flush=True)
    print(f"Games folder: {launcher.settings['games_dir']}", flush=True)
    print("Keep this window open while the launcher runs; press Ctrl+C to stop it.", flush=True)
    open_ui(url, args.browser)

    def remind():
        time.sleep(12)
        if not launcher.connected:
            print(f"No browser has opened the page yet. Paste this address into any browser: {url}", flush=True)
            print("Or start with --browser default to use the system browser, or --browser none to only print the address.", flush=True)

    threading.Thread(target=remind, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        launcher.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        traceback.print_exc()
        code = 1
        if WINDOWS:
            try:
                input("The launcher stopped with the error above. Press Enter to close this window.")
            except (EOFError, OSError):
                pass
    sys.exit(code)
