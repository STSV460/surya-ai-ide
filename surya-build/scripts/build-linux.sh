#!/usr/bin/env bash
# Build Surya AI Code for Linux (Ubuntu) inside the docker builder.
# Produces: dist/linux/surya-ai-code_{ver}_amd64.deb and a .AppImage.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FORK="$ROOT/Surya AI Code Linux"
UPSTREAM="$FORK/upstream"
DIST="$ROOT/dist/linux"
mkdir -p "$DIST"

cd "$UPSTREAM"

# Embed python-build-standalone runtime so the agent-core can run on user machines.
PY_BUNDLE="extensions/surya-ai/agent-core/python"
mkdir -p "$PY_BUNDLE"
if [ -d /opt/surya-python ] && [ ! -f "$PY_BUNDLE/bin/python3" ]; then
  rsync -a /opt/surya-python/ "$PY_BUNDLE/"
  "$PY_BUNDLE/bin/python3" -m pip install --no-cache-dir \
    "crewai>=0.86,<0.90" "crewai-tools>=0.17" "openai>=1.50" \
    "pydantic>=2.0,<2.6" "httpx>=0.27" "gitpython>=3.1" "playwright>=1.45"
fi

echo ">> yarn install"
yarn --frozen-lockfile || yarn

echo ">> compile builtin extensions"
yarn gulp compile-build || true
yarn gulp compile-extensions-build || true

echo ">> build linux x64"
yarn gulp vscode-linux-x64-min

echo ">> build .deb"
yarn gulp vscode-linux-x64-build-deb || true
find ../.. -name "surya-ai-code_*.deb" -exec cp {} "$DIST/" \; || true

echo ">> stage AppDir + AppImage"
APPDIR="$DIST/Surya-AI-Code.AppDir"
rm -rf "$APPDIR" && mkdir -p "$APPDIR/usr"
cp -r "../../VSCode-linux-x64"/* "$APPDIR/usr/" 2>/dev/null || cp -r "/work/VSCode-linux-x64"/* "$APPDIR/usr/"
cp "$ROOT/surya-build/branding/linux/surya-512.png" "$APPDIR/surya-ai-code.png"
cat > "$APPDIR/surya-ai-code.desktop" <<EOF
[Desktop Entry]
Name=Surya AI Code
Exec=surya-ai-code
Icon=surya-ai-code
Type=Application
Categories=Development;IDE;
StartupWMClass=surya-ai-code
EOF
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/surya-ai-code" "$@"
EOF
chmod +x "$APPDIR/AppRun"
ARCH=x86_64 appimagetool "$APPDIR" "$DIST/Surya-AI-Code-x86_64.AppImage" || true

echo ">> done. Artifacts in $DIST:"
ls -la "$DIST"
