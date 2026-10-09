#!/usr/bin/env python3
"""Builds a single-file Windows .exe using PyInstaller + Pillow for the icon.
Called by .github/workflows/build-windows.yml after packages are installed.
VERSION env var sets the filename; falls back to 0.0.0."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

img = Image.open("docs/icon.png")
img.save(
    "privatiser.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)

version = os.environ.get("VERSION", "0.0.0")
safe_version = version.replace("~", "-")
exe_stem = f"Privatiser-{safe_version}-windows"

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "--name", exe_stem,
        "--onefile",
        "--windowed",
        "--collect-data", "PyQt6",
        "--icon", "privatiser.ico",
        "main.py",
    ],
    check=True,
)

src = Path("dist") / f"{exe_stem}.exe"
shutil.move(str(src), f"{exe_stem}.exe")
print(f"Built: {exe_stem}.exe")
