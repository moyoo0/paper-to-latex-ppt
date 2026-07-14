#!/usr/bin/env python3
"""Check runtime dependencies for paper-to-latex-ppt."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path


PYTHON_MODULES = {
    "fitz": "pymupdf",
    "pptx": "python-pptx",
    "yaml": "pyyaml",
}

COMMANDS = ["latexmk", "xelatex"]


def find_command(command: str) -> tuple[str | None, bool]:
    path = shutil.which(command)
    if path:
        return path, True

    home = Path.home()
    candidates = [
        home / "Library" / "TinyTeX" / "bin" / "universal-darwin" / command,
        home / ".TinyTeX" / "bin" / "universal-darwin" / command,
        home / "bin" / command,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate), False
    return None, False


def main() -> None:
    missing_modules = []
    missing_commands = []
    path_warnings = []

    print("Python:", sys.executable)
    for module, package in PYTHON_MODULES.items():
        if importlib.util.find_spec(module):
            print(f"[OK] Python module: {module}")
        else:
            print(f"[MISSING] Python module: {module} ({package})")
            missing_modules.append(package)

    for command in COMMANDS:
        path, in_path = find_command(command)
        if path:
            status = "OK" if in_path else "FOUND_NOT_IN_PATH"
            print(f"[{status}] Command: {command} -> {path}")
            if not in_path:
                path_warnings.append(Path(path).parent)
        else:
            print(f"[MISSING] Command: {command}")
            missing_commands.append(command)

    if missing_modules:
        print("\nInstall Python dependencies:")
        print("  python3 -m pip install -r requirements.txt")

    if missing_commands:
        print("\nInstall LaTeX runtime:")
        print("  macOS TinyTeX:")
        print("    curl -fsSL https://yihui.org/tinytex/install-bin-unix.sh | sh")
        print("  Then ensure TinyTeX's bin directory is in PATH.")

    if path_warnings:
        unique_dirs = sorted({str(path) for path in path_warnings})
        print("\nLaTeX tools were found but are not in PATH for this shell.")
        for directory in unique_dirs:
            print(f"  export PATH=\"$PATH:{directory}\"")
        print("Add the export line to ~/.zshrc or run it before using this skill.")

    if missing_modules or missing_commands or path_warnings:
        raise SystemExit(1)

    print("\nEnvironment looks ready.")


if __name__ == "__main__":
    main()
