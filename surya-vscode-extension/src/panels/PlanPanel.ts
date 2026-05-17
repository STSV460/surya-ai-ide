import * as vscode from "vscode";
import { Sidecar } from "../sidecar";
import { onPlanUpdate } from "../tools/bridge";
import { renderHtml } from "./html";

export class PlanPanel implements vscode.WebviewViewProvider {
  constructor(private ctx: vscode.ExtensionContext, private sidecar: Sidecar) {}

  resolveWebviewView(view: vscode.WebviewView) {
    view.webview.options = { enableScripts: true };
    view.webview.html = renderHtml("Plan", `<pre id="plan" style="white-space:pre-wrap"></pre>
      <script>
        const vscode = acquireVsCodeApi();
        window.addEventListener('message', e => {
          if (e.data.type === 'plan') document.getElementById('plan').textContent = e.data.text;
        });
      </script>`);
    const sub = onPlanUpdate((p) => {
      view.webview.postMessage({ type: "plan", text: JSON.stringify(p, null, 2) });
    });
    view.onDidDispose(() => sub.dispose());
  }
}
