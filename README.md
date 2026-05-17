# Surya AI IDE

VS Code fork modeled on Google Antigravity, powered by a **CrewAI hierarchical 9-agent crew** with every LLM call routed through the **InsForge Model Gateway** (Opus 4.7, Sonnet 4.6, GPT, Gemini, more).

## OS support
- macOS — current + future (Sequoia/Tahoe and forward)
- Windows — **Win 7, 8/8.1, 10, 11** and forward (fork pinned to VS Code 1.70 / Electron 22 for Win 7)
- Linux — **Ubuntu** only (22.04 LTS, 24.04 LTS, future LTS)

## Repo layout
```
Surya AI Code Mac/         macOS fork of VS Code (Code-OSS) — upstream/ is gitignored
Surya AI Code Windows/     Windows fork (Win 7 compatible build)
Surya AI Code Linux/       Linux fork (Ubuntu only)
surya-agent-core/          Shared CrewAI Python sidecar
surya-vscode-extension/    Shared TS extension + webview panels
surya-build/               Build scripts, branding (icons), Dockerfiles
docs/                      Architecture and build notes
```

## 9-agent crew
Architect · Planner · Researcher · Implementer · Coder · Builder · Reviewer · Tester · Verifier
Manager LLM = `anthropic/claude-opus-4-7`.

## Quota
Claude Code / Codex-style **rolling 5-hour usage window** per user, every model. Tiers: Free 50 pts · Pro 500 pts · Max 2500 pts. Enforced in `surya-agent-core/surya/quota.py` against InsForge DB table `user_quota`.

## Build (per fork)
```bash
# 1. clone vscode into the fork
git clone --depth 1 [--branch release/1.70] https://github.com/microsoft/vscode.git "Surya AI Code <OS>/upstream"

# 2. rebrand + embed Surya extension/agent
python3 surya-build/scripts/rebrand.py "Surya AI Code <OS>" <mac|win|linux>
bash    surya-build/scripts/sync.sh    "Surya AI Code <OS>"

# 3. build (in the fork's upstream/)
cd "Surya AI Code <OS>/upstream"
yarn
yarn gulp vscode-<platform>
```

## InsForge link
```
npx @insforge/cli login --user-api-key <uak_...>
npx @insforge/cli link  --project-id 34f28c7e-362b-4157-81f3-6039212f583c
```
