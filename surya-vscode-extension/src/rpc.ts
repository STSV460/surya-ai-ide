import { Readable, Writable } from "stream";

type Pending = { resolve: (v: any) => void; reject: (e: any) => void };

export class RpcClient {
  private buf = Buffer.alloc(0);
  private pending = new Map<number, Pending>();
  private nextId = 1;

  constructor(
    private rx: Readable,
    private tx: Writable,
    private onRequest: (method: string, params: any) => Promise<any>,
  ) {
    rx.on("data", (chunk: Buffer) => this.onData(chunk));
  }

  call(method: string, params: any): Promise<any> {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.send({ jsonrpc: "2.0", id, method, params });
    });
  }

  private send(msg: any) {
    const data = Buffer.from(JSON.stringify(msg), "utf-8");
    this.tx.write(`Content-Length: ${data.length}\r\n\r\n`);
    this.tx.write(data);
  }

  private onData(chunk: Buffer) {
    this.buf = Buffer.concat([this.buf, chunk]);
    while (true) {
      const headerEnd = this.buf.indexOf("\r\n\r\n");
      if (headerEnd === -1) return;
      const header = this.buf.slice(0, headerEnd).toString();
      const m = /Content-Length:\s*(\d+)/i.exec(header);
      if (!m) { this.buf = this.buf.slice(headerEnd + 4); continue; }
      const n = parseInt(m[1], 10);
      if (this.buf.length < headerEnd + 4 + n) return;
      const body = this.buf.slice(headerEnd + 4, headerEnd + 4 + n).toString("utf-8");
      this.buf = this.buf.slice(headerEnd + 4 + n);
      try { this.dispatch(JSON.parse(body)); } catch (e) { console.error("rpc parse", e); }
    }
  }

  private async dispatch(msg: any) {
    if (msg.method && typeof msg.id !== "undefined") {
      try {
        const result = await this.onRequest(msg.method, msg.params || {});
        this.send({ jsonrpc: "2.0", id: msg.id, result });
      } catch (e: any) {
        this.send({ jsonrpc: "2.0", id: msg.id, error: { code: -32000, message: String(e?.message || e) }});
      }
    } else if (typeof msg.id !== "undefined") {
      const p = this.pending.get(msg.id); this.pending.delete(msg.id);
      if (!p) return;
      if (msg.error) p.reject(msg.error); else p.resolve(msg.result);
    }
  }
}
