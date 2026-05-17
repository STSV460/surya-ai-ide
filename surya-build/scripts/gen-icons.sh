#!/usr/bin/env bash
# Generate Mac (.icns), Windows (.ico), Linux PNG set, and extension icon
# from surya-build/branding/surya-logo.png (square source, >=512px).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/surya-build/branding/surya-logo.png"
OUT="$ROOT/surya-build/branding"

[ -f "$SRC" ] || { echo "missing $SRC"; exit 1; }

# Use 1024 master if present, else create
MASTER="$OUT/surya-logo-1024.png"
[ -f "$MASTER" ] || sips -z 1024 1024 "$SRC" --out "$MASTER" >/dev/null

# ---------- Mac .icns ----------
ICONSET="$OUT/surya.iconset"
rm -rf "$ICONSET" && mkdir -p "$ICONSET"
for sz in 16 32 64 128 256 512; do
  sips -z "$sz" "$sz" "$MASTER" --out "$ICONSET/icon_${sz}x${sz}.png"     >/dev/null
  sips -z "$((sz*2))" "$((sz*2))" "$MASTER" --out "$ICONSET/icon_${sz}x${sz}@2x.png" >/dev/null
done
sips -z 1024 1024 "$MASTER" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET" -o "$OUT/surya.icns"
rm -rf "$ICONSET"
echo "wrote $OUT/surya.icns"

# ---------- Windows .ico ----------
TMP_ICO_DIR="$OUT/.ico_tmp"
rm -rf "$TMP_ICO_DIR" && mkdir -p "$TMP_ICO_DIR"
for sz in 16 24 32 48 64 128 256; do
  sips -z "$sz" "$sz" "$MASTER" --out "$TMP_ICO_DIR/${sz}.png" >/dev/null
done
if command -v magick >/dev/null 2>&1; then
  magick "$TMP_ICO_DIR"/{16,24,32,48,64,128,256}.png "$OUT/surya.ico"
elif command -v convert >/dev/null 2>&1; then
  convert "$TMP_ICO_DIR"/{16,24,32,48,64,128,256}.png "$OUT/surya.ico"
elif command -v png2icns >/dev/null 2>&1; then
  echo "no ImageMagick — install with: brew install imagemagick"
else
  echo "WARN: no ImageMagick. Install: brew install imagemagick. Skipping .ico."
fi
rm -rf "$TMP_ICO_DIR"
[ -f "$OUT/surya.ico" ] && echo "wrote $OUT/surya.ico"

# ---------- Linux multi-res PNG ----------
LINUX="$OUT/linux"
mkdir -p "$LINUX"
for sz in 16 32 48 64 128 256 512; do
  sips -z "$sz" "$sz" "$MASTER" --out "$LINUX/surya-${sz}.png" >/dev/null
done
cp "$MASTER" "$LINUX/surya-1024.png"
echo "wrote $LINUX/surya-*.png"

# ---------- Extension icon (replace SVG) ----------
EXT_MEDIA="$ROOT/surya-vscode-extension/media"
mkdir -p "$EXT_MEDIA"
sips -z 256 256 "$MASTER" --out "$EXT_MEDIA/surya-icon.png" >/dev/null
echo "wrote $EXT_MEDIA/surya-icon.png"
