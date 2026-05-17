import * as vscode from "vscode";
import { Sidecar } from "./sidecar";
import { ChatPanel } from "./panels/ChatPanel";
import { AgentsPanel } from "./panels/AgentsPanel";
import { PlanPanel } from "./panels/PlanPanel";
import { registerBridgeHandlers } from "./tools/bridge";

const INSFORGE_KEY_SECRET = "surya.insforgeApiKey";

export async function activate(context: vscode.ExtensionContext) {
  const sidecar = new Sidecar(context);
  await ensureSignedIn(context);
  await sidecar.start();
  registerBridgeHandlers(sidecar);

  const chat   = new ChatPanel(context, sidecar);
  const agents = new AgentsPanel(context, sidecar);
  const plan   = new PlanPanel(context, sidecar);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("surya-ai.chat",   chat),
    vscode.window.registerWebviewViewProvider("surya-ai.agents", agents),
    vscode.window.registerWebviewViewProvider("surya-ai.plan",   plan),

    vscode.commands.registerCommand("surya-ai.run", async () => {
      const goal = await vscode.window.showInputBox({ prompt: "Surya AI — what should the crew build?" });
      if (!goal) return;
      const res = await sidecar.call("run", { goal });
      if (res && res.error === "QUOTA_EXCEEDED") {
        const mins = Math.ceil((res.resets_in_s || 0) / 60);
        vscode.window.showWarningMessage(`Surya quota reached (${res.used.toFixed(0)}/${res.limit.toFixed(0)} pts). Resets in ${mins}m.`);
      } else {
        chat.appendResult(res);
      }
    }),

    vscode.commands.registerCommand("surya-ai.signIn", () => signIn(context)),

    vscode.commands.registerCommand("surya-ai.restartAgent", async () => {
      await sidecar.restart();
      vscode.window.showInformationMessage("Surya agent sidecar restarted.");
    }),
  );

  context.subscriptions.push({ dispose: () => sidecar.stop() });
}

export function deactivate() {}

async function ensureSignedIn(context: vscode.ExtensionContext) {
  const key = await context.secrets.get(INSFORGE_KEY_SECRET);
  if (!key) await signIn(context);
}

async function signIn(context: vscode.ExtensionContext) {
  const key = await vscode.window.showInputBox({
    prompt: "Paste your InsForge user API key (uak_...)",
    password: true,
    ignoreFocusOut: true,
  });
  if (!key) {
    vscode.window.showErrorMessage("Surya AI: InsForge key required to use the crew.");
    return;
  }
  await context.secrets.store(INSFORGE_KEY_SECRET, key);
  vscode.window.showInformationMessage("Surya AI: signed in.");
}
