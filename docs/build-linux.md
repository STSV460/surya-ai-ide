# Linux Build — Docker on Mac

Builds Surya AI Code Linux (Ubuntu .deb + .AppImage) inside an Ubuntu 22.04 docker container. Works from this Mac, no Linux machine needed.

## 1. Prereqs on Mac
```bash
brew install --cask docker     # if not already
open -a Docker                  # start Docker Desktop
```

## 2. Build the builder image (~10 min, one-time)
```bash
cd "/Volumes/Prabhas SSD/Surya AI/Surya AI IDE"
docker build -f surya-build/docker/linux-builder.Dockerfile -t surya-linux-builder .
```

## 3. Run the build (~20-40 min)
```bash
docker run --rm -it \
  -v "$PWD":/work -w /work \
  surya-linux-builder \
  bash surya-build/scripts/build-linux.sh
```

Outputs land in `dist/linux/`:
- `surya-ai-code_<ver>_amd64.deb`
- `Surya-AI-Code-x86_64.AppImage`

## 4. Sign the apt repo (one-time GPG key)
```bash
gpg --quick-gen-key "Surya AI <pvshariharan324@gmail.com>" rsa4096 default 5y
gpg --export -a "Surya AI" > surya-build/branding/surya-apt.asc

# Sign the .deb
dpkg-sig --sign builder dist/linux/*.deb
```

## 5. Local install test
On any Ubuntu 22.04/24.04 box (or another docker container):
```bash
sudo dpkg -i surya-ai-code_*.deb
sudo apt-get -f install   # pulls deps if missing
surya-ai-code
```

For AppImage: `chmod +x *.AppImage && ./Surya-AI-Code-x86_64.AppImage`.
