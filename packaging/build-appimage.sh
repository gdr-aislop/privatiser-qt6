#!/bin/bash
# Builds a cross-distro AppImage.
# Called by .github/workflows/build-appimage.yml after system deps and a
# Python venv have already been set up by earlier workflow steps.
# PY and PYINSTALLER env vars point into the venv; fall back to bare names
# for local testing.
set -euo pipefail

PY="${PY:-python3}"
PYINSTALLER="${PYINSTALLER:-pyinstaller}"

"$PYINSTALLER" \
    --name privatiser \
    --onedir \
    --windowed \
    --collect-data PyQt6 \
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

install -m 755 packaging/AppRun             "${APPDIR}/AppRun"
install -m 644 packaging/privatiser.desktop "${APPDIR}/privatiser.desktop"
install -m 644 privatiser.png               "${APPDIR}/privatiser.png"

# Download appimagetool (itself an AppImage; use APPIMAGE_EXTRACT_AND_RUN=1
# to avoid needing FUSE)
wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
    -O appimagetool
chmod +x appimagetool

VERSION="${VERSION:-0.0.0}"
APPIMAGE_NAME="Privatiser-${VERSION}-x86_64.AppImage"

UPDATE_INFO="gh-releases-zsync|gdr-aislop|privatiser-qt6|latest|Privatiser-*-x86_64.AppImage.zsync"

APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 \
    ./appimagetool -u "${UPDATE_INFO}" Privatiser.AppDir "${APPIMAGE_NAME}"

zsyncmake "${APPIMAGE_NAME}"

echo "Built: ${APPIMAGE_NAME}"
