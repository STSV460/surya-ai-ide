# Windows Build — UTM VM Setup (Apple Silicon Mac)

Goal: build Surya AI Code Windows (VS Code 1.70 fork, Electron 22, Win 7+ compatible) on this Mac.

VS Code Windows build **must** run on Windows. Cross-build from macOS not supported. Use a free UTM Windows VM.

## 1. Install UTM (free)
```
brew install --cask utm
```
Or download from https://mac.getutm.app/

## 2. Get Windows 11 ARM (Apple Silicon)
- Apple Silicon Mac: install Windows 11 ARM. Free dev preview from Microsoft Insider program: https://www.microsoft.com/en-us/software-download/windowsinsiderpreviewARM64
- Build target = `win32-x64` though, so we also need x64 emulation OR cross-build via wine inside the VM. Simpler: also install Windows 10/11 x64 in a second UTM VM with QEMU x86_64 (slow but works).
- Practical alternative: cheap x64 Windows mini-PC (~₹15-25K) for ongoing builds; UTM for one-off.

## 3. Inside the Windows VM, install build prereqs
PowerShell as admin:
```powershell
# Install scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Tools
scoop install git python@3.8.10 nodejs-lts@16 yarn innosetup
scoop install gh

# VS Code 1.70 build needs:
npm install -g node-gyp
```

Install **Visual Studio Build Tools 2019** (for native modules on Electron 22):
https://visualstudio.microsoft.com/visual-cpp-build-tools/  → workload "Desktop development with C++".

## 4. Clone repo + fork
```powershell
gh auth login
git clone https://github.com/STSV460/surya-ai-ide.git
cd surya-ai-ide
git clone --depth 1 --branch release/1.70 https://github.com/microsoft/vscode.git "Surya AI Code Windows\upstream"
python surya-build\scripts\rebrand.py "Surya AI Code Windows" win
bash surya-build\scripts\sync.sh "Surya AI Code Windows"   # use Git Bash
```

## 5. Build
```powershell
cd "Surya AI Code Windows\upstream"
yarn
yarn gulp vscode-win32-x64-min
yarn gulp vscode-win32-ia32-min   # 32-bit for old Win 7 boxes
```

Output under `..\VSCode-win32-x64\` and `..\VSCode-win32-ia32\`.

## 6. Sign
```powershell
# Replace <CERT> with your EV cert path / thumbprint
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "..\VSCode-win32-x64\Surya AI Code.exe"
```

## 7. Installer (Inno Setup 6.2)
Open `build/win32/code.iss` (already rebranded by the rebrand script). Compile via Inno Setup. Output: `Surya-AI-Code-Setup-x64.exe`.

## 8. Test matrix
- Run installer on Win 7 SP1 VM, Win 8.1, Win 10, Win 11 — confirm Surya panel works.
- Top-50 marketplace extensions install + activate without error.

## Cost summary
- UTM: free
- Windows 11 ARM Insider: free for dev use
- Visual Studio Build Tools: free
- Inno Setup: free
- EV code-signing cert: ~₹20-25K/yr (DigiCert/Sectigo). Skip for dev builds; SmartScreen warns users but they can click through.
