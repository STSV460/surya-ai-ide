"""Entry point for the Surya agent-core sidecar.

VS Code extension spawns this as a child process and speaks JSON-RPC over stdio.
"""
from __future__ import annotations
import threading
from typing import Any, Dict

from .config import RuntimeConfig
from .crew import run_task
from .quota import QuotaClient, QuotaExceeded
from .rpc import RpcServer


def main() -> None:
    cfg = RuntimeConfig.from_env()
    server: RpcServer  # forward ref

    def bridge_send(method: str, params: Dict[str, Any]) -> Any:
        return server.call(method, params)

    def h_ping(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "agents": 9}

    def h_run(params: Dict[str, Any]) -> Dict[str, Any]:
        goal = params.get("goal", "")
        if not goal:
            raise ValueError("missing 'goal'")
        try:
            return run_task(cfg, bridge_send, goal)
        except QuotaExceeded as e:
            return {"error": "QUOTA_EXCEEDED", "used": e.used,
                    "limit": e.limit, "resets_in_s": e.resets_in}

    def h_quota_status(_: Dict[str, Any]) -> Dict[str, Any]:
        qc = QuotaClient(cfg.api_key)
        s = qc.status(cfg.user_id)
        return {"tier": s.tier, "used": s.points_used,
                "limit": s.limit, "resets_in_s": s.resets_in,
                "bypass": s.bypass}

    server = RpcServer(handlers={
        "ping": h_ping,
        "run":  h_run,
        "quota.status": h_quota_status,
    })

    threading.current_thread().name = "surya-rpc-main"
    server.serve_forever()


if __name__ == "__main__":
    main()
