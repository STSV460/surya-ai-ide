import * as vscode from "vscode";
import * as cp from "child_process";
import * as path from "path";
import * as os from "os";
import { RpcClient } from "./rpc";

const INSFORGE_KEY_SECRET = "surya.insforgeApiKey";

type BridgeHandler = (params: any) => Promise<any> | any;

export class Sidecar {
  private proc?: cp.ChildProcessWithoutNullStreams;
  private rpc?: RpcClient;
  private handlers = new Map<string, BridgeHandler>();
  private restartTimer?: NodeJS.Timeout;

  constructor(private context: vscode.ExtensionContext) {}

  registerHandler(method: string, fn: BridgeHandler) {
    this.handlers.set(method, fn);
  }

  async start() {
    const key = await this.context.secrets.get(INSFORGE_KEY_SECRET);
    if (!key) {
      vscode.window.showWarningMessage("Surya AI: not signed in. Run `Surya AI: Sign in`.");
      return;
    }
    const cfg = vscode.workspace.getConfiguration("surya");
    const userId = cfg.get<string>("userId") || os.userInfo().username || "anonymous";
    const ws = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || os.homedir();

    const env = {
      ...process.env,
      INSFORGE_API_KEY: key,
      SURYA_USER_ID: userId,
      SURYA_WORKSPACE_ROOT: ws,
      PYTHONUNBUFFERED: "1",
    };

    const py = this.resolvePython();
    const coreDir = path.join(this.context.extensionPath, "agent-core");
    this.proc = cp.spawn(py, ["-m", "surya"], { env, cwd: coreDir });
    this.proc.stderr.on("data", d => console.error("[surya]", d.toString()));
    this.proc.on("exit", code => {
      console.warn("[surya] sidecar exit", code);
      if (!this.restartTimer) {
        this.restartTimer = setTimeout(() => { this.restartTimer = undefined; this.start(); }, 2000);
      }
    });

    this.rpc = new RpcClient(this.proc.stdout, this.proc.stdin, async (method, params) => {
      const h = this.handlers.get(method);
      if (!h) throw new Error(`unknown bridge method: ${method}`);
      return await h(params);
    });

    try { await this.rpc.call("ping", {}); }
    catch (e) { console.warn("[surya] ping failed", e); }
  }

  async restart() { this.stop(); await this.start(); }

  stop() {
    try { this.proc?.kill(); } catch {}
    this.proc = undefined;
    this.rpc = undefined;
  }

  async call(method: string, params: any): Promise<any> {
    if (!this.rpc) throw new Error("Surya sidecar not ready");
    return this.rpc.call(method, params);
  }

  private resolvePython(): string {
    // Bundled python-build-standalone shipped alongside the agent-core under extension/agent-core/python/
    const ext = process.platform === "win32" ? ".exe" : "";
    const bundled = path.join(this.context.extensionPath, "agent-core", "python", "bin", "python3" + ext);
    return bundled;
  }
}
