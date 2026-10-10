# Launcher development and handoff

User documentation: [docs/user/LAUNCHER.md](../user/LAUNCHER.md). This page is for whoever works on the launcher next, and ends with what it takes to run large titles such as GTA V and GTA VI.

## Files

| File | Role |
|------|------|
| [launcher/anyps5_launcher.py](../../launcher/anyps5_launcher.py) | Back end. Python 3 standard library only (as the rest of `tools/`). HTTP server on `127.0.0.1`, JSON API, library scan, conversion jobs, process control, settings. |
| [launcher/ui/index.html](../../launcher/ui/index.html) | Page shell: top bar, screens, side menu, control center, dialog, toasts, hint bar. The server replaces `__TOKEN__` on every load. |
| [launcher/ui/style.css](../../launcher/ui/style.css) | PS5 look and the `data-theme` overrides for `ps4`, `ps3` and `ps1`. No external fonts or images; icons are inline SVG. |
| [launcher/ui/app.js](../../launcher/ui/app.js) | Front end: state, API client, spatial focus navigation, gamepad polling, screens, dialogs, themes and synthesized sounds. |
| [tools/tests/test_launcher.py](../../tools/tests/test_launcher.py) | Unit tests, registered as the `launcher` ctest in [CMakeLists.txt](../../CMakeLists.txt). |
| [tools/build_package.py](../../tools/build_package.py) | Copies `launcher/`, `tools/import_audit.py`, `tools/nid_names.py` and writes `AnyPS5.cmd` and `AnyPS5.sh` into the package. |

## How it works

1. **Discovery**: `Launcher.scan()` walks the games folder two levels deep. A folder counts as a title when it has `sce_sys/` or an executable. `inspect_source()` reads `sce_sys/param.json` (`titleId`, `localizedParameters[defaultLanguage].titleName`, `contentId`, `contentVersion`), finds the executable (`eboot.bin` first, then any ELF), the module directory (`sce_module`, `sce_modules` or `prx`) and `icon0.png` / `pic0.png`, and checks the executable's magic: `7f 45 4c 46` is a clean ELF, `4f 15 3d 1d` is a SELF container that the relinker cannot take. Installed builds whose dump disappeared are listed from `<install>/<id>/install.json`.
2. **Install**: `Launcher.install()` builds the relinker command from the global settings and per-conversion options (`conversion_command()`), always adds `--registry` so the audit has input, streams the output into a job, then creates the [runtime layout](../user/USAGE.md#runtime-layout): `app0/<entry>` links for every top-level entry of the dump except the executable and the module directory (the relinker already wrote the converted modules under `app0/`), `libs/` to the system libraries, `anyps5-fonts/` when configured. `link_entry()` tries a symbolic link, then a junction (Windows, via `_winapi.CreateJunction`), then a hard link, then a copy. `install.json` records the source, command and options.
3. **Launch**: `Launcher.launch()` starts `app.elf` / `app.exe` with the install folder as working directory (the runtime resolves `/app0` against the current directory, see `core/libs/prx/libc/src/General.cpp`) and the environment from `environment()`: `ANYPS5_GPU`, `ANYPS5_SYSTEM_FONTS`, `ANYPS5_NO_SHADER_CACHE`, `ANYPS5_SHADER_CACHE_DIR`, `ANYPS5_ENTITLEMENTS`, `ANYPS5_REQUIRE_VULKAN`, `ANYPS5_REQUIRE_DISPLAY`, plus per-title overrides from `games.json`. Output goes to `anyps5-launcher.log`. A watcher thread records the exit code, play time and the last line that looks like an error (`what()`, `terminate called`, `FAIL`) into `stats.json`.
4. **Audit**: runs `tools/import_audit.py` on the `*.registry.json` files with `--libs`, `--modules` and `--source core/libs/prx` when the source tree is present (a package has no source tree, so stubs are then counted as implemented; the job says so). The result is `audit.json` in the install folder and feeds the Compatibility card.
5. **Front end**: every interactive element has `data-focus`; `move(direction)` picks the geometrically nearest candidate in the top-most layer (dialog, control center, side menu, screen). Keyboard, the Gamepad API (standard mapping: 0 ✕, 1 ○, 3 △, 16 PS) and mouse hover all drive the same focus. `refresh()` polls `/api/state` every 2.5 s and turns new server notifications into toasts. Themes are `data-theme` on `<html>`; `applyTheme()` injects the PS4 streaks, the XMB ribbon SVG or the PS1 diamond into `#bgTheme`, and `sound()` plays the theme's note table through the Web Audio API.

### API

All endpoints are under `/api/` and require the `X-AnyPS5-Token` header (or `t=` query for image URLs); the token is random per process and embedded in the page, so other origins cannot call the API. Errors are HTTP 400 with `{"error": ...}`.

| Method | Endpoint | Body or query | Returns |
|--------|----------|---------------|---------|
| GET | `state` | | settings, games, running, notifications, host, jobs |
| GET | `job` | `id` | job with `status` (`running`, `done`, `failed`), `log`, `result`, `error` |
| GET | `log` | `id` | last 400 lines of the title's log |
| GET | `audit` | `id` | last `audit.json` |
| GET | `icon`, `art` | `id`, `t` | PNG |
| GET | `input` | `id` | `anyps5-input.ini` text and the action list |
| GET | `gpus` | | device names from `vulkaninfo --summary` and from logs |
| GET | `inspect` | `source` | `inspect_source()` result |
| GET | `docs` | | bundled `docs/*.md` |
| POST | `settings` | subset of `DEFAULT_SETTINGS` | saved settings |
| POST | `scan`, `launch`, `stop`, `remove`, `save-backup`, `clear-shader-cache`, `quit` | `id` where needed | |
| POST | `install` | `source`, `options` | job id |
| POST | `audit` | `id` | job id |
| POST | `open` | `id` + `what` (`source`, `run`, `save`, `config`) or `path` | opens the folder in the file manager |
| POST | `pick-folder` | `title` | path from the native folder dialog (PowerShell, osascript, zenity or kdialog) |
| POST | `input` | `id`, `text` | validates with `validate_input_config()` |
| POST | `game-settings` | `id`, `overrides` | |
| POST | `setup-relinker` | | job id; downloads the latest package (release assets, else the newest successful Package workflow artifact on `main`) into `AnyPS5-<platform>/` beside the launcher |
| POST | `build-package` | | job id; runs `tools/build_package.py` |
| GET | `console-list` | `path` | folders and files on the console's FTP server (MLSD, falling back to LIST) |
| POST | `console-import` | `path`, `install` | job id; downloads the folder into the games folder and, with `install`, converts it |
| POST | `decrypt-merge` | `source`, `decrypted`, `install` | job id; replaces every SELF in the dump with the matching decrypted ELF from `decrypted`, backs up the originals to `_self_backup/` and, with `install`, converts the dump |

The Package workflow also publishes the two package zips as a rolling `latest` pre-release on every push to `main`, so `setup-relinker` keeps working after the 90-day artifact expiry. The GitHub token is never returned by the API; `state` reports it as `set`.

Config folder: `%APPDATA%\AnyPS5` or `~/.config/anyps5` with `launcher.json`, `stats.json`, `games.json`, `backups/` and the app-mode browser profile.

## Testing

- Unit tests: `python3 tools/tests/test_launcher.py` (also `ctest -R launcher`).
- Manual run without a built relinker: create a dump folder with `sce_sys/param.json`, a file starting with `7f 45 4c 46` named `eboot.bin` and an `sce_module/` directory; point Settings › Paths › relinker at a script that writes the output file and prints `Guest module:` lines, and the libraries path at a folder with `*.prx` files. The install, launch, log, stop, input, backup, remove and theme flows were verified this way on Linux with a Python relinker stand-in and Chromium screenshots.
- Conventions: `python3 tools/check_conventions.py --base origin/main`. Python files may not contain `#` outside strings; `.svg`, `.png` and other images are rejected; new `.md` files are only accepted under `docs/user`, `docs/dev` and `.github`; commit subjects follow Conventional Commits.

## Open items

- **Windows is untested**: the `.cmd` start script, `py` detection, the PowerShell folder dialog, junction creation and `--windows-gui` conversions were written for Windows but the development container was Linux. Test on Windows first. The launcher itself starts and serves its page on Windows (confirmed by the repository owner).
- **Console import is tested against a local FTP server only** (pyftpdlib, MLSD and LIST). Real PS5 FTP payloads differ in LIST output and in whether they support MLSD; the parser handles the Unix `ls -l` form. The dumps folder on the console depends on the dumper used, so `ps5_path` is a setting.
- **Decryption runs on the console**: the launcher has no keys and decrypts nothing itself. *Decrypt a Dump* (`decryptWizard()` in `app.js`) shows a risk warning, sends the decrypter payload from Settings › Console and calls `decrypt-merge`. `self_files()` finds SELF containers among the dump's top-level `.bin`, `.elf`, `.self`, `.prx` and `.sprx` files and inside the module folder; `inspect_source()` reports encrypted modules as well as an encrypted executable. `match_decrypted()` matches by file name (also with a trailing `.elf`, `.dec` or `.decrypted`), ranks a candidate whose path ends with the dump-relative path and contains the title ID first, and refuses a tie. Verified only against synthetic dumps and a synthetic `PS5/system_ex/app/<id>/` USB tree; check the real decrypter's output layout on a console.
- **Browser gamepad**: the Gamepad API only reports a pad after a button press and some browsers hide DualSense until then; inside games SDL handles pads independently.
- **Audit without source tree**: a package cannot classify throwing stubs. Either ship a generated stub list with the package or teach `import_audit.py` to read a precomputed `stubs.json`.
- **App window**: `--browser app` uses a Chromium `--app=` window; a native window (for example a small SDL or Qt shell) would remove the browser dependency. Keep the HTTP API if you do.
- **Possible additions**: per-title conversion option overrides on reinstall, a captures folder for screenshots once the runtime can take them, several profiles, PS2 and PSP themes, trophy display from `sce_sys/trophy2`.

## What it takes to run GTA V and GTA VI

The launcher only starts what the relinker and the system libraries can run. Both titles are far outside what the project runs today ([compatibility list](../user/COMPATIBILITY.md)), and the blockers are in this order:

1. **A clean ELF dump of the PS5 version.** The relinker needs the decrypted executable and modules (`4f 15 3d 1d` SELF containers are rejected, see [usage](../user/USAGE.md#input-and-conversion)). This project ships no keys and no decryption, by design (README disclaimer). A dump comes from your own console with a firmware that has a public exploit. GTA VI is not released as of October 2026 and will require the current system software, which has no public exploit, so there is no legal or technical way to obtain its ELF; any claim that it runs on this project is false. GTA V (PS5 edition) can only be dumped from a console on exploitable firmware that the title accepts.
2. **Missing system functions.** Install the dump through the launcher and run the import audit. Every `absent` import stops the title at load; every `stub` throws when called. Each one has to be implemented with its real behaviour in `core/libs/prx/<library>` following [CONTRIBUTING](../../CONTRIBUTING.md): no silent stubs, generic behaviour, a throw on anything unsupported. A title of this size imports thousands of functions across audio (`libSceAudioOut`, `libSceAudio3d`, `libSceNgs2`), video (`libSceVideoOut` VRR and HDR, `libSceAvPlayer`), save data, trophies, network and platform services, so expect a long iteration: launch, read the throw in the launcher's Last session card, implement, relaunch.
3. **Shader recompiler coverage.** The AGC shader ISA translation in `core/shader/recompiler` has to handle every instruction, resource type and pipeline stage the title's shaders use (geometry, tessellation, compute, wave operations). Unsupported instructions throw at pipeline creation; each needs semantics verified with the [hardware oracle](HW_ORACLE.md) and recorded per [TechnicalDebt](TechnicalDebt.md).
4. **Graphics driver features.** `libSceAgcDriver` must cover the title's command-buffer usage (multiple queues, async compute, tiled resources, DCC, indirect draws). The progress badges on the project page measure how much of the known surface is done.
5. **CPU and memory.** `--to-intel` converts AMD-only instructions; a title that uses instructions the converter does not know fails conversion with the offset, which has to be added in `core/relinker/codegen`. Direct memory (up to 13.8 GiB) is committed in full on Windows, so 32 GiB of RAM plus page file is the realistic minimum.
6. **Performance** is the last concern: the converted program runs natively, so once it runs, the cost is in shader translation and driver emulation, not CPU emulation.

Realistic expectation: GTA V is a multi-month to multi-year engineering target for this architecture, gated first by obtaining a legal dump. GTA VI cannot be attempted until it is released, dumpable and its firmware exploited, which is not foreseeable.
