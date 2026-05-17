#!/usr/bin/env python3
"""Apply Surya AI Code rebrand to a fork's upstream/ tree.

Usage:
  python3 rebrand.py "Surya AI Code Mac"     mac
  python3 rebrand.py "Surya AI Code Windows" win
  python3 rebrand.py "Surya AI Code Linux"   linux
"""
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / "surya-build" / "branding"


PRODUCT_PATCH = {
    "nameShort": "Surya AI Code",
    "nameLong":  "Surya AI Code",
    "applicationName": "surya-ai-code",
    "dataFolderName": ".surya-ai-code",
    "win32MutexName": "suryaaicode",
    "win32DirName":   "Surya AI Code",
    "win32NameVersion": "Surya AI Code",
    "win32RegValueName": "SuryaAICode",
    "win32AppId":     "{{F7B2D9C5-7C9D-4A1F-9F11-3B3B7D7D9F11}}",
    "win32x64AppId":  "{{F7B2D9C5-7C9D-4A1F-9F11-3B3B7D7D9F12}}",
    "win32UserAppId": "{{F7B2D9C5-7C9D-4A1F-9F11-3B3B7D7D9F13}}",
    "win32Userx64AppId": "{{F7B2D9C5-7C9D-4A1F-9F11-3B3B7D7D9F14}}",
    "win32AppUserModelId": "Surya.AICode",
    "win32ShellNameShort": "Surya AI Code",
    "darwinBundleIdentifier": "ai.surya.code",
    "linuxIconName": "surya-ai-code",
    "licenseName": "Proprietary",
    "urlProtocol": "surya-ai-code",
    "serverApplicationName": "surya-ai-code-server",
    "serverDataFolderName": ".surya-ai-code-server",
    "extensionsGallery": {
        "serviceUrl":   "https://marketplace.visualstudio.com/_apis/public/gallery",
        "cacheUrl":     "https://vscode.blob.core.windows.net/gallery/index",
        "itemUrl":      "https://marketplace.visualstudio.com/items",
        "publisherUrl": "https://marketplace.visualstudio.com/publishers",
        "resourceUrlTemplate": "https://{publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/{publisher}/extension/{name}/{version}/assetbyname/{path}",
        "controlUrl": "",
        "recommendationsUrl": "",
        "fallbackServiceUrl": "https://open-vsx.org/vscode/gallery",
        "fallbackItemUrl":    "https://open-vsx.org/vscode/item",
    },
}


def patch_product_json(upstream: Path) -> None:
    p = upstream / "product.json"
    data = json.loads(p.read_text())
    data.update(PRODUCT_PATCH)
    p.write_text(json.dumps(data, indent=2) + "\n")
    print(f"patched {p}")


def copy_icons(upstream: Path, platform: str) -> None:
    if platform == "mac":
        dst = upstream / "resources" / "darwin" / "code.icns"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BRAND / "surya.icns", dst); print(f"icon -> {dst}")
    elif platform == "win":
        dst = upstream / "resources" / "win32" / "code.ico"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BRAND / "surya.ico", dst); print(f"icon -> {dst}")
        for sz in (70, 150):
            src = BRAND / "linux" / f"surya-{ {70:64,150:128}[sz] }.png"
            if src.exists():
                shutil.copy2(src, upstream / "resources" / "win32" / f"code_{sz}x{sz}.png")
    elif platform == "linux":
        d = upstream / "resources" / "linux"
        d.mkdir(parents=True, exist_ok=True)
        for src in (BRAND / "linux").glob("surya-*.png"):
            sz = src.stem.split("-")[1]
            shutil.copy2(src, d / f"code-{sz}.png")
        shutil.copy2(BRAND / "linux" / "surya-512.png", d / "code.png")
        print(f"linux icons -> {d}")


def main():
    if len(sys.argv) != 3:
        print("usage: rebrand.py <fork-dir-name> <mac|win|linux>"); sys.exit(2)
    fork = ROOT / sys.argv[1]
    platform = sys.argv[2]
    upstream = fork / "upstream"
    if not upstream.exists():
        print(f"no upstream at {upstream}"); sys.exit(1)
    patch_product_json(upstream)
    copy_icons(upstream, platform)
    print(f">> rebrand done: {fork} ({platform})")


if __name__ == "__main__":
    main()
