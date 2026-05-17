# Surya AI Code — Linux builder image (Ubuntu 22.04 baseline).
# Builds the rebranded VS Code fork into .deb + .AppImage.
#
# Build:
#   docker build -f surya-build/docker/linux-builder.Dockerfile -t surya-linux-builder .
# Run (from repo root):
#   docker run --rm -it -v "$PWD":/work -w /work surya-linux-builder bash surya-build/scripts/build-linux.sh

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=20.18.0
ENV YARN_VERSION=1.22.22

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates git build-essential python3 python3-pip \
      libx11-dev libxkbfile-dev libsecret-1-dev libkrb5-dev \
      libnss3 libnotify4 libasound2 libgbm1 \
      fakeroot rpm desktop-file-utils file rsync xz-utils \
      gnupg dpkg-sig dpkg-dev apt-utils \
    && rm -rf /var/lib/apt/lists/*

# Node + Yarn
RUN curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /opt && ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/node /usr/local/bin/node \
      && ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/npm  /usr/local/bin/npm \
      && ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/npx  /usr/local/bin/npx \
      && npm install -g yarn@${YARN_VERSION}

# Python-build-standalone (3.12) for bundling into Surya .deb
RUN curl -fsSL -o /tmp/python.tar.gz \
      "https://github.com/indygreg/python-build-standalone/releases/download/20240909/cpython-3.12.6+20240909-x86_64-unknown-linux-gnu-install_only.tar.gz" \
    && mkdir -p /opt/surya-python && tar -xzf /tmp/python.tar.gz -C /opt/surya-python --strip-components=1 \
    && rm /tmp/python.tar.gz

# AppImage tooling
RUN curl -fsSL -o /usr/local/bin/appimagetool \
      https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x /usr/local/bin/appimagetool

WORKDIR /work
