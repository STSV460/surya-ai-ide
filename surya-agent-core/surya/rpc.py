"""JSON-RPC 2.0 framing over stdio.

Frame format (LSP-style):
  Content-Length: <N>\r\n\r\n<JSON of N bytes>
"""
from __future__ import annotations
import json
import sys
import threading
from typing import Any, Callable, Dict, Optional


class RpcServer:
    def __init__(self, handlers: Dict[str, Callable[[Dict[str, Any]], Any]]):
        self.handlers = handlers
        self._send_lock = threading.Lock()
        self._next_id = 1
        self._pending: Dict[int, "threading.Event"] = {}
        self._results: Dict[int, Any] = {}
        self._stop = False

    def _read_message(self) -> Optional[Dict[str, Any]]:
        stdin = sys.stdin.buffer
        headers: Dict[str, str] = {}
        while True:
            line = stdin.readline()
            if not line:
                return None
            if line in (b"\r\n", b"\n"):
                break
            if b":" in line:
                k, _, v = line.partition(b":")
                headers[k.decode().strip().lower()] = v.decode().strip()
        n = int(headers.get("content-length", "0"))
        if n <= 0:
            return None
        body = stdin.read(n)
        return json.loads(body)

    def _write(self, msg: Dict[str, Any]) -> None:
        data = json.dumps(msg).encode("utf-8")
        with self._send_lock:
            out = sys.stdout.buffer
            out.write(f"Content-Length: {len(data)}\r\n\r\n".encode())
            out.write(data)
            out.flush()

    def call(self, method: str, params: Dict[str, Any]) -> Any:
        rid = self._next_id
        self._next_id += 1
        ev = threading.Event()
        self._pending[rid] = ev
        self._write({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        ev.wait(timeout=120)
        return self._results.pop(rid, None)

    def serve_forever(self) -> None:
        while not self._stop:
            msg = self._read_message()
            if msg is None:
                break
            if "method" in msg and "id" in msg:
                self._handle_request(msg)
            elif "method" in msg:
                self._handle_notification(msg)
            elif "id" in msg:
                self._handle_response(msg)

    def _handle_request(self, msg: Dict[str, Any]) -> None:
        method = msg["method"]
        params = msg.get("params") or {}
        handler = self.handlers.get(method)
        try:
            if handler is None:
                raise RuntimeError(f"unknown method: {method}")
            result = handler(params)
            self._write({"jsonrpc": "2.0", "id": msg["id"], "result": result})
        except Exception as e:
            self._write({"jsonrpc": "2.0", "id": msg["id"],
                         "error": {"code": -32000, "message": str(e)}})

    def _handle_notification(self, msg: Dict[str, Any]) -> None:
        handler = self.handlers.get(msg["method"])
        if handler:
            try:
                handler(msg.get("params") or {})
            except Exception:
                pass

    def _handle_response(self, msg: Dict[str, Any]) -> None:
        rid = msg["id"]
        self._results[rid] = msg.get("result") if "result" in msg else msg.get("error")
        ev = self._pending.pop(rid, None)
        if ev:
            ev.set()
