#!/bin/bash
# Builds a macOS DMG.
# Called by .github/workflows/build-dmg.yml after a Python venv has been
# set up by earlier workflow steps.
# PY and PYINSTALLER env vars point into the venv; fall back to bare names
# for local testing.
set -euo pipefail

PY="${PY:-python3}"
PYINSTALLER="${PYINSTALLER:-pyinstaller}"

# Build privatiser.icns from docs/icon.png using built-in macOS tools
mkdir -p privatiser.iconset
sips -z 16 16     docs/icon.png --out privatiser.iconset/icon_16x16.png      >/dev/null
sips -z 32 32     docs/icon.png --out privatiser.iconset/icon_16x16@2x.png   >/dev/null
sips -z 32 32     docs/icon.png --out privatiser.iconset/icon_32x32.png      >/dev/null
sips -z 64 64     docs/icon.png --out privatiser.iconset/icon_32x32@2x.png   >/dev/null
sips -z 128 128   docs/icon.png --out privatiser.iconset/icon_128x128.png    >/dev/null
sips -z 256 256   docs/icon.png --out privatiser.iconset/icon_128x128@2x.png >/dev/null
sips -z 256 256   docs/icon.png --out privatiser.iconset/icon_256x256.png    >/dev/null
sips -z 512 512   docs/icon.png --out privatiser.iconset/icon_256x256@2x.png >/dev/null
sips -z 512 512   docs/icon.png --out privatiser.iconset/icon_512x512.png    >/dev/null
sips -z 1024 1024 docs/icon.png --out privatiser.iconset/icon_512x512@2x.png >/dev/null
iconutil -c icns privatiser.iconset -o privatiser.icns

"$PYINSTALLER" \
    --name Privatiser \
    --onedir \
    --windowed \
    --collect-data PyQt6 \
    --icon privatiser.icns \
    main.py

VERSION="${VERSION:-0.0.0}"
# Sanitize version for use in filename (~gitSHORT → -gitSHORT)
SAFE_VERSION="${VERSION//\~/-}"
DMG_NAME="Privatiser-${SAFE_VERSION}-macOS.dmg"

# Stage: .app + Applications symlink for drag-to-install UX
mkdir -p dmg_staging
cp -r dist/Privatiser.app dmg_staging/
ln -s /Applications dmg_staging/Applications

hdiutil create \
    -volname "Privatiser ${VERSION}" \
    -srcfolder dmg_staging \
    -ov \
    -format UDZO \
    "${DMG_NAME}"

echo "Built: ${DMG_NAME}"
