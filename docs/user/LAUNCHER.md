# Launcher

The launcher is a PlayStation-style front end for the relinker on a PC. It finds title dumps, converts them with `relinker`, lays out the [runtime layout](USAGE.md#runtime-layout) for each title, starts the converted executable and shows what happened. It is a Python 3 program that serves its interface to a browser window on `127.0.0.1`; nothing leaves the machine.

## Start

In a [prebuilt package](../dev/BUILD.md#prebuilt-package) or a [one-command build](../dev/BUILD.md#one-command-build):

```text
AnyPS5.cmd   (Windows)
./AnyPS5.sh  (Linux)
```

From the repository, with `relinker` built in `build/` and the `libs` target built:

```sh
python3 launcher/anyps5_launcher.py
```

Python 3.8 or newer is required. With Chrome, Edge, Chromium or Brave installed, the interface opens in a borderless window; otherwise it opens in the default browser. Press `F` or `F11` for fullscreen.

| Option | Effect |
|--------|--------|
| `--port <n>` | Listen on another port. The default is 7355, or a free port when it is taken. |
| `--config <dir>` | Settings, play statistics, per-title overrides and save-data backups. Defaults to `%APPDATA%\AnyPS5` on Windows and `~/.config/anyps5` elsewhere. |
| `--browser auto\|app\|default\|none` | `app` forces the borderless window, `default` the system browser, `none` only prints the address. |
| `--verbose` | Log every request. |

The relinker and the system libraries are found next to the launcher (package layout), in `build/`, or at the paths set in Settings › Paths.

## Folders

Settings › Paths names two folders:

- **Games folder**: one sub-folder per title dump. A dump holds the clean ELF executable (`eboot.bin` or another ELF), `sce_sys/param.json` for the title name and ID, and the bundled modules in `sce_module/`, `sce_modules/` or `prx/`, as in [usage](USAGE.md#input-and-conversion). Sub-folders one level deeper are scanned too. Dumps that still contain a SELF container are listed with the problem and cannot be converted.
- **Installed builds folder**: one sub-folder per title ID with the [runtime layout](USAGE.md#runtime-layout): `app.elf` or `app.exe`, `app0/` with the converted modules and links to the dump's files, `libs/` linked to the system libraries, `anyps5-fonts/` when a fonts folder is set, the launch log `anyps5-launcher.log`, the `*.registry.json` files and the save data in `_sd/`.

Resources are symbolic links, directory junctions or hard links, so the dump stays the single copy; Settings › Conversion › *Copy resources instead of linking* copies them instead.

## Screens

- **Games**: the home screen. Tiles for every title, the selected title's status, verified compatibility from [COMPATIBILITY.md](COMPATIBILITY.md), the last session's exit code and throw message, controls and save data. ✕ plays an installed title or installs one; △ opens the title menu.
- **Title menu** (△ or *Options*): play, install or reinstall, import audit, log, controller and keyboard mapping, per-title settings, save-data backup, open folders, remove the installed build.
- **Homebrew**: package installer, import audit, logs, controller mapper, save-data manager, shader cache, GPU selector, debug settings, library, documentation, system information, themes.
- **Package Installer**: choose a dump folder, see what was detected, set the relinker options for this conversion and watch the relinker output.
- **Settings**: paths, conversion defaults (`--to-intel` automatic from the host CPU, `unused-filter`, `--windows-gui`, `--rpath`), graphics (`ANYPS5_GPU`, shader cache), runtime environment, the deprecated debug flags, interface and system information.
- **Control Center** (PS button, `P` or `Home`): running title, notifications, sound, controllers, fullscreen, theme, profile, settings, power.

## Controls

| Action | Controller | Keyboard |
|--------|------------|----------|
| Move | D-pad, left stick | Arrow keys, Tab |
| Select | ✕ | Enter, Space |
| Back | ○ | Escape, Backspace |
| Title menu | △ | T |
| Control Center | PS, Options | P, Home |
| Scroll a page | Right stick | Page Up, Page Down, mouse wheel |
| Fullscreen | | F, F11 |
| Next theme | | Y |

Controllers are read through the browser's Gamepad API; press a button once after connecting. Inside games, controllers are handled by SDL as described in [input mapping](INPUT_MAPPING.md); the launcher's controller mapper edits that `anyps5-input.ini` per title and validates every line before saving.

## Themes

Settings › Interface › Theme, the Homebrew *Themes* tile and the Control Center switch between four looks, each with its own synthesized menu sounds: **PS5** (key art, glass cards), **PS4** (blue dynamic menu), **PS3 · XMB** (the ribbon, with the background colour following the month) and **PS1** (bevelled panels, scanlines and chiptune bleeps). No original console assets are used.

## What runs

The launcher changes nothing about which titles run. A converted title runs as far as the [system libraries](../dev/ARCHITECTURE.md) implement the functions it imports; a missing import stops it at start with the message shown in the launcher's *Last session* card and log, and a throwing stub stops it when the title calls that function. Run the **import audit** on an installed title to see, before launching, how many imports are implemented, stubbed or absent. The [compatibility list](COMPATIBILITY.md) names the titles verified so far. What it takes to run a large title is described in [launcher development](../dev/LAUNCHER.md#what-it-takes-to-run-gta-v-and-gta-vi).
