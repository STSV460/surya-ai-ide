import * as vscode from "vscode";
import { Sidecar } from "../sidecar";
import { renderHtml } from "./html";

export class ChatPanel implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;
  constructor(private ctx: vscode.ExtensionContext, private sidecar: Sidecar) {}

  resolveWebviewView(view: vscode.WebviewView) {
    this.view = view;
    view.webview.options = { enableScripts: true };
    view.webview.html = renderHtml("Chat", `
      <textarea id="goal" placeholder="What should the Surya crew build?" rows="4" style="width:100%"></textarea>
      <button id="go">Run</button>
      <div id="quota" style="margin-top:8px;opacity:.7;font-size:11px"></div>
      <pre id="out" style="white-space:pre-wrap;margin-top:12px"></pre>
      <script>
        const vscode = acquireVsCodeApi();
        document.getElementById('go').onclick = () => {
          const g = document.getElementById('goal').value;
          vscode.postMessage({ type: 'run', goal: g });
        };
        window.addEventListener('message', e => {
          if (e.data.type === 'result') document.getElementById('out').textContent = JSON.stringify(e.data.result, null, 2);
          if (e.data.type === 'quota')  document.getElementById('quota').textContent = e.data.text;
        });
        setInterval(() => vscode.postMessage({ type: 'quota' }), 30000);
        vscode.postMessage({ type: 'quota' });
      </script>
    `);

    view.webview.onDidReceiveMessage(async (msg) => {
      if (msg.type === "run") {
        const result = await this.sidecar.call("run", { goal: msg.goal });
        view.webview.postMessage({ type: "result", result });
      } else if (msg.type === "quota") {
        try {
          const q = await this.sidecar.call("quota.status", {});
          const mins = Math.ceil((q.resets_in_s || 0) / 60);
          view.webview.postMessage({
            type: "quota",
            text: `${q.tier.toUpperCase()} · ${q.used.toFixed(0)}/${q.limit.toFixed(0)} pts · resets in ${mins}m`,
          });
        } catch {}
      }
    });
  }

  appendResult(result: any) {
    this.view?.webview.postMessage({ type: "result", result });
  }
}
