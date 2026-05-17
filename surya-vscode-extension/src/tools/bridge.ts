import * as vscode from "vscode";
import { Sidecar } from "../sidecar";

let planEmitter = new vscode.EventEmitter<any>();
export const onPlanUpdate = planEmitter.event;

export function registerBridgeHandlers(sidecar: Sidecar) {
  sidecar.registerHandler("editor.openFile", async (p) => {
    const doc = await vscode.workspace.openTextDocument(p.path);
    await vscode.window.showTextDocument(doc);
    return { ok: true };
  });

  sidecar.registerHandler("editor.applyDiff", async (p) => {
    const uri = vscode.Uri.file(p.path);
    const we = new vscode.WorkspaceEdit();
    we.createFile(uri, { overwrite: true, ignoreIfExists: false });
    we.insert(uri, new vscode.Position(0, 0), p.content || "");
    await vscode.workspace.applyEdit(we);
    return { ok: true };
  });

  sidecar.registerHandler("terminal.run", async (p) => {
    const term = vscode.window.createTerminal({ name: "Surya AI" });
    term.show(true);
    term.sendText(p.command);
    return { ok: true };
  });

  sidecar.registerHandler("ui.notify", async (p) => {
    const kind = p.kind || "info";
    if (kind === "error") vscode.window.showErrorMessage(p.message);
    else if (kind === "warn") vscode.window.showWarningMessage(p.message);
    else vscode.window.showInformationMessage(p.message);
    return { ok: true };
  });

  sidecar.registerHandler("plan.update", async (p) => {
    planEmitter.fire(p);
    return { ok: true };
  });
}
