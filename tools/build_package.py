import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = os.name == "nt"
PLATFORM = "windows" if WINDOWS else "linux"
MINGW_RUNTIME = ("libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll")
GIT_CA_BUNDLE = Path("C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt")
LAUNCHER = ROOT / "launcher"
LAUNCHER_NAME = "AnyPS5.exe" if WINDOWS else "AnyPS5"


def run(command, env=None):
    print("+", " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], cwd=ROOT, check=True, env=env)


def require_tools():
    missing = [tool for tool in ("git", "cmake", "ninja", "gcc", "g++") if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"Missing on PATH: {', '.join(missing)}. See docs/dev/BUILD.md")


def build(build_dir, build_type, jobs):
    require_tools()
    run(["git", "submodule", "update", "--init", "--recursive"])
    env = dict(os.environ)
    if WINDOWS and "SSL_CERT_FILE" not in env and GIT_CA_BUNDLE.is_file():
        env["SSL_CERT_FILE"] = str(GIT_CA_BUNDLE)
    configure = ["cmake", "-S", ROOT, "-B", build_dir, "-G", "Ninja", f"-DCMAKE_BUILD_TYPE={build_type}",
                 "-DCMAKE_C_COMPILER=gcc", "-DCMAKE_CXX_COMPILER=g++"]
    if shutil.which("ccache"):
        configure += ["-DCMAKE_C_COMPILER_LAUNCHER=ccache", "-DCMAKE_CXX_COMPILER_LAUNCHER=ccache"]
    run(configure, env)
    parallel = ["--parallel", str(jobs)] if jobs else ["--parallel"]
    run(["cmake", "--build", build_dir, *parallel])
    run(["cmake", "--build", build_dir, "--target", "libs", *parallel])


def launcher_available():
    return importlib.util.find_spec("PyInstaller") is not None and importlib.util.find_spec("webview") is not None


def build_launcher(build_dir):
    if not launcher_available():
        raise RuntimeError("Building the launcher needs pywebview and PyInstaller: python -m pip install -r launcher/requirements.txt pyinstaller")
    work = build_dir / "launcher"
    dist = work / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    sys.path.insert(0, str(LAUNCHER))
    import make_icon

    icon = make_icon.build(work / "AnyPS5.ico")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--name", "AnyPS5",
               "--distpath", dist, "--workpath", work / "work", "--specpath", work,
               "--add-data", f"{LAUNCHER / 'ui'}{os.pathsep}ui", "--icon", icon, LAUNCHER / "anyps5_launcher.py"]
    run(command)
    built = dist / "AnyPS5" / LAUNCHER_NAME
    if not built.is_file():
        raise RuntimeError(f"PyInstaller did not produce {built}")
    return built.parent


def assemble(build_dir, output, launcher_dir=None):
    executable = build_dir / "core/relinker" / ("relinker.exe" if WINDOWS else "relinker")
    libraries = sorted((build_dir / "core/libs/libs").glob("*.prx"))
    expected = {f"{directory.name}.prx" for directory in (ROOT / "core/libs/prx").iterdir() if directory.is_dir()}
    missing = expected - {library.name for library in libraries}
    if missing:
        raise RuntimeError(f"Missing system libraries: {', '.join(sorted(missing))}; build the libs target")
    if not executable.is_file():
        raise RuntimeError(f"Missing relinker: {executable}")
    runtime = []
    if WINDOWS:
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("g++ must be on PATH to locate the MinGW runtime DLLs")
        runtime = [Path(compiler).parent / name for name in MINGW_RUNTIME]
        absent = [str(file) for file in runtime if not file.is_file()]
        if absent:
            raise RuntimeError(f"Missing MinGW runtime: {', '.join(absent)}")
    if output.exists():
        shutil.rmtree(output)
    (output / "libs").mkdir(parents=True)
    (output / "docs").mkdir()
    shutil.copy2(executable, output / executable.name)
    for file in [*libraries, *runtime]:
        shutil.copy2(file, output / "libs" / file.name)
    for document in sorted((ROOT / "docs/user").glob("*.md")):
        shutil.copy2(document, output / "docs" / document.name)
    shutil.copy2(ROOT / "LICENSE", output / "LICENSE")
    if launcher_dir is not None:
        shutil.copytree(launcher_dir, output, dirs_exist_ok=True)
    print(f"Package ready: {output} ({len(libraries)} libraries{', launcher ' + LAUNCHER_NAME if launcher_dir else ''})")


def main():
    parser = argparse.ArgumentParser(description="Build AnyPS5 and collect relinker plus system libraries into one folder")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--output", type=Path, default=ROOT / f"AnyPS5-{PLATFORM}")
    parser.add_argument("--build-type", default="Release", choices=("Debug", "Release", "RelWithDebInfo", "MinSizeRel"))
    parser.add_argument("--jobs", type=int, default=0)
    parser.add_argument("--skip-build", action="store_true", help="Only assemble an existing build")
    parser.add_argument("--launcher", choices=("auto", "on", "off"), default="auto",
                        help="Build the AnyPS5 launcher with PyInstaller: auto (when pywebview and PyInstaller are installed), on, off")
    args = parser.parse_args()
    build_dir = args.build_dir.resolve()
    try:
        if not args.skip_build:
            build(build_dir, args.build_type, args.jobs)
        launcher_dir = None
        if args.launcher == "on" or (args.launcher == "auto" and launcher_available()):
            launcher_dir = build_launcher(build_dir)
        elif args.launcher == "auto":
            print("Launcher skipped: install pywebview and PyInstaller to include AnyPS5" + (".exe" if WINDOWS else ""))
        assemble(build_dir, args.output.resolve(), launcher_dir)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
