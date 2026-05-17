from __future__ import annotations
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess
from ..config import RuntimeConfig


class _Args(BaseModel):
    args: str = Field(..., description="Git args, e.g. 'status' or 'diff HEAD'.")


class GitTool(BaseTool):
    name: str = "git"
    description: str = "Run a git command in the workspace root."
    args_schema: type = _Args

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()
        self._cwd = cfg.workspace_root

    def _run(self, args: str) -> str:
        r = subprocess.run(f"git {args}", shell=True, cwd=self._cwd,
                           capture_output=True, text=True, timeout=60)
        return f"exit={r.returncode}\n{r.stdout}{r.stderr}"


def make_tool(cfg): return GitTool(cfg)
