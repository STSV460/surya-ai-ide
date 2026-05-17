from __future__ import annotations
from typing import Any, Callable, Dict
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class _Args(BaseModel):
    method: str = Field(..., description="VS Code bridge method (e.g. 'editor.openFile', 'terminal.run', 'ui.notify').")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method params.")


class VSCodeBridgeTool(BaseTool):
    name: str = "vscode_bridge"
    description: str = (
        "Call back into the Surya VS Code extension over JSON-RPC. "
        "Methods: editor.openFile, editor.applyDiff, terminal.run, ui.notify, ui.progress, plan.update."
    )
    args_schema: type = _Args

    def __init__(self, send: Callable[[str, Dict[str, Any]], Any]):
        super().__init__()
        self._send = send

    def _run(self, method: str, params: Dict[str, Any] = None) -> str:
        try:
            res = self._send(method, params or {})
            return f"OK: {res}"
        except Exception as e:
            return f"ERROR: {e}"


def make_tool(send_fn): return VSCodeBridgeTool(send_fn)
