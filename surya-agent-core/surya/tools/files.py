from __future__ import annotations
import os
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..config import RuntimeConfig


def _resolve(root: str, rel: str) -> Path:
    p = (Path(root) / rel).resolve()
    if not str(p).startswith(str(Path(root).resolve())):
        raise ValueError(f"path escapes workspace: {rel}")
    return p


class _ReadArgs(BaseModel):
    path: str = Field(..., description="Workspace-relative file path to read.")


class ReadTool(BaseTool):
    name: str = "file_read"
    description: str = "Read a UTF-8 text file from the workspace."
    args_schema: type = _ReadArgs

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()
        self._root = cfg.workspace_root

    def _run(self, path: str) -> str:
        p = _resolve(self._root, path)
        if not p.exists():
            return f"NOT_FOUND: {path}"
        return p.read_text(encoding="utf-8", errors="replace")


class _WriteArgs(BaseModel):
    path: str = Field(..., description="Workspace-relative file path.")
    content: str = Field(..., description="Full new file content.")


class WriteTool(BaseTool):
    name: str = "file_write"
    description: str = "Write (or overwrite) a UTF-8 text file in the workspace."
    args_schema: type = _WriteArgs

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()
        self._root = cfg.workspace_root

    def _run(self, path: str, content: str) -> str:
        p = _resolve(self._root, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"WROTE {path} ({len(content)} bytes)"


class _ListArgs(BaseModel):
    path: str = Field(".", description="Workspace-relative dir to list.")


class ListTool(BaseTool):
    name: str = "file_list"
    description: str = "List immediate entries in a workspace directory."
    args_schema: type = _ListArgs

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()
        self._root = cfg.workspace_root

    def _run(self, path: str = ".") -> str:
        p = _resolve(self._root, path)
        if not p.is_dir():
            return f"NOT_A_DIR: {path}"
        return "\n".join(sorted(os.listdir(p)))


def make_read_tool(cfg):  return ReadTool(cfg)
def make_write_tool(cfg): return WriteTool(cfg)
def make_list_tool(cfg):  return ListTool(cfg)
