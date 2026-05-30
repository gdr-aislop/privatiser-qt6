#!/bin/bash
# Runs inside ubuntu:24.04 (glibc 2.39, Python 3.12) to produce an AppImage.
# Called by .github/workflows/build-appimage.yml via docker run.
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y --no-install-recommends \
    python3 python3-venv python3-dev \
    binutils patchelf \
    wget \
    imagemagick \
    libxcb-cursor0 libxcb1 libx11-6 libgl1 libglib2.0-0

# Use a venv to avoid PEP 668 "externally-managed-environment" errors
# on Ubuntu 24.04 and to keep pip independent of the system package manager.
python3 -m venv /opt/build-venv
/opt/build-venv/bin/pip install --quiet --upgrade pip
/opt/build-venv/bin/pip install --quiet PyQt6 privatiser pyinstaller

/opt/build-venv/bin/pyinstaller \
    --name privatiser \
    --onedir \
    --windowed \
    --collect-all PyQt6 \
    main.py

# Placeholder icon — replace docs/icon.png in the repo to override
if [ -f docs/icon.png ]; then
    cp docs/icon.png privatiser.png
else
    convert -size 256x256 xc:'#4682B4' -fill white \
        -font DejaVu-Sans -pointsize 64 -gravity center \
        -annotate 0 'P' privatiser.png 2>/dev/null \
    || convert -size 256x256 xc:'#4682B4' privatiser.png
fi

# Assemble AppDir
APPDIR="Privatiser.AppDir"
mkdir -p "${APPDIR}/usr/bin"
cp -r dist/privatiser/. "${APPDIR}/usr/bin/"

install -m 755 packaging/AppRun          "${APPDIR}/AppRun"
install -m 644 packaging/privatiser.desktop "${APPDIR}/privatiser.desktop"
install -m 644 privatiser.png             "${APPDIR}/privatiser.png"

# Download appimagetool (itself an AppImage; use APPIMAGE_EXTRACT_AND_RUN=1
# to avoid needing FUSE inside Docker)
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
    -O appimagetool
chmod +x appimagetool

VERSION="${VERSION:-0.0.0}"
APPIMAGE_NAME="Privatiser-${VERSION}-x86_64.AppImage"

APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 \
    ./appimagetool Privatiser.AppDir "${APPIMAGE_NAME}"

echo "Built: ${APPIMAGE_NAME}"
