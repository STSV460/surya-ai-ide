from __future__ import annotations
import subprocess
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..config import RuntimeConfig


class _Args(BaseModel):
    command: str = Field(..., description="Shell command to run in workspace root.")
    timeout_s: int = Field(120, description="Timeout in seconds.")


class ShellTool(BaseTool):
    name: str = "shell"
    description: str = "Run a shell command in the workspace root. Returns stdout+stderr."
    args_schema: type = _Args

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()
        self._cwd = cfg.workspace_root

    def _run(self, command: str, timeout_s: int = 120) -> str:
        try:
            r = subprocess.run(
                command, shell=True, cwd=self._cwd, capture_output=True,
                text=True, timeout=timeout_s,
            )
            return f"exit={r.returncode}\n--stdout--\n{r.stdout}\n--stderr--\n{r.stderr}"
        except subprocess.TimeoutExpired:
            return f"timeout after {timeout_s}s"


def make_tool(cfg: RuntimeConfig) -> ShellTool:
    return ShellTool(cfg)
