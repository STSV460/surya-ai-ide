import * as vscode from "vscode";
import { Sidecar } from "../sidecar";
import { renderHtml } from "./html";

const AGENTS = [
  ["Architect",   "Opus 4.7"],
  ["Planner",     "Sonnet 4.6"],
  ["Researcher",  "Gemini Flash"],
  ["Implementer", "Sonnet 4.6"],
  ["Coder",       "Sonnet 4.6"],
  ["Builder",     "Sonnet 4.6"],
  ["Reviewer",    "Opus 4.7"],
  ["Tester",      "Sonnet 4.6"],
  ["Verifier",    "Opus 4.7"],
];

export class AgentsPanel implements vscode.WebviewViewProvider {
  constructor(private ctx: vscode.ExtensionContext, private sidecar: Sidecar) {}

  resolveWebviewView(view: vscode.WebviewView) {
    view.webview.options = { enableScripts: true };
    const rows = AGENTS.map(([name, model]) =>
      `<tr><td style="padding:4px 8px">${name}</td><td style="opacity:.7">${model}</td></tr>`
    ).join("");
    view.webview.html = renderHtml("Agents", `
      <p style="opacity:.7;font-size:12px">9-agent hierarchical crew. Manager: Opus 4.7.</p>
      <table style="border-collapse:collapse;width:100%">${rows}</table>
    `);
  }
}
