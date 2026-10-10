# AnyPS5 launcher

`AnyPS5.exe` is the desktop application in the [Windows package](../dev/BUILD.md#prebuilt-package). It keeps a library of games, converts each one with the [relinker](USAGE.md) on its first start, and runs it with the system libraries from the package. The conversion runs once; later starts are immediate.

## Add a game

Drop the game folder onto the window, or press **Add game** and pick it. The folder is the one that holds the executable (`eboot.bin`) and its bundled modules (`sce_module/`, `sce_modules/` or `prx/`), as described in [usage](USAGE.md#input-and-conversion). A folder that contains that folder also works. The title, title ID and icon are read from `sce_sys/param.json` and `sce_sys/icon0.png` when present.

The game folder is never modified except for the converted modules, which the relinker writes beside the originals as `<module>.guest.prx`.

## Play

Press **Play**. On the first start the launcher runs `relinker --windows` (with `--to-intel` on Intel processors) and writes `app.exe` and the links `app0` and `libs` into the launcher's own folder for that game. A later change to `eboot.bin`, to the relinker, or to the game's options converts it again; **Rebuild** forces a new conversion.

Everything the relinker and the game print appears in the **Log** panel, including the Vulkan devices found at start-up and the error a game throws when it stops. **Copy** puts the log on the clipboard for a bug report.

**Stop** ends the game. Closing the launcher stops every running game.

## Options

Each game has its own options; Settings holds the defaults for new games.

| Option | Effect |
|--------|--------|
| Instruction conversion | `Automatic` adds `--to-intel` on Intel processors. `Always` and `Never` override the detection. |
| GPU | Part of a Vulkan device name, used as `ANYPS5_GPU` (see [GPU selection](USAGE.md#gpu-selection)). |
| Input mapping file | An `anyps5-input.ini`, used as `ANYPS5_INPUT_CONFIG` (see [input mapping](INPUT_MAPPING.md)). |

## Files

The library, the converted executables and the logs are in `%LOCALAPPDATA%\AnyPS5` on Windows (`~/.local/share/anyps5` on Linux); **Open** in Settings shows the folder. Set `ANYPS5_LAUNCHER_HOME` to use another folder. Each game has a folder `games/<id>/` with `app.exe`, `convert.json`, `game.log`, and `app0` and `libs` as directory junctions to the game folder and to the package's `libs/`. Removing a game from the library deletes this folder and leaves the game folder alone.

The relinker and `libs/` are found next to `AnyPS5.exe`. Settings can point to other copies, which is how the launcher runs from a source checkout: `relinker` from `build/core/relinker/` and the libraries from `build/core/libs/libs/`.

## Run from source

```sh
python -m pip install -r launcher/requirements.txt
python launcher/anyps5_launcher.py
```

The launcher is [pywebview](https://pywebview.flowrl.com/) on top of the `launcher/ui` HTML files; on Windows it uses the WebView2 runtime that ships with Windows 10 and 11. On Linux pywebview needs GTK (`pywebview[gtk]`) or Qt (`pywebview[qt]`), and the Linux package does not include a launcher executable. [Building](../dev/BUILD.md#launcher) describes how the executable is made.
