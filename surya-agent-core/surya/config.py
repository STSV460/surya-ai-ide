"""Surya agent-core config. All LLM calls route through InsForge Model Gateway."""
from __future__ import annotations
import os
from dataclasses import dataclass

INSFORGE_PROJECT_ID = "34f28c7e-362b-4157-81f3-6039212f583c"

INSFORGE_GATEWAY_BASE = os.environ.get(
    "INSFORGE_GATEWAY_BASE",
    f"https://api.insforge.dev/v1/projects/{INSFORGE_PROJECT_ID}/ai/openai",
)

MODEL_MANAGER = "anthropic/claude-opus-4-7"

MODEL_BY_AGENT = {
    "architect":   "anthropic/claude-opus-4-7",
    "planner":     "anthropic/claude-sonnet-4-6",
    "researcher":  "google/gemini-flash-latest",
    "implementer": "anthropic/claude-sonnet-4-6",
    "coder":       "anthropic/claude-sonnet-4-6",
    "builder":     "anthropic/claude-sonnet-4-6",
    "reviewer":    "anthropic/claude-opus-4-7",
    "tester":      "anthropic/claude-sonnet-4-6",
    "verifier":    "anthropic/claude-opus-4-7",
}

# Point cost weights per 1K output tokens. Input tokens half-weighted.
MODEL_POINT_COST = {
    "anthropic/claude-opus-4-7":   5.0,
    "anthropic/claude-sonnet-4-6": 2.0,
    "google/gemini-pro-latest":    2.0,
    "google/gemini-flash-latest":  1.0,
    "openai/gpt-5":                4.0,
    "openai/gpt-4o":               2.0,
}

TIER_LIMITS = {
    "free": 50,
    "pro":  500,
    "max":  2500,
}

QUOTA_WINDOW_SECONDS = 5 * 60 * 60  # 5 hours

@dataclass(frozen=True)
class RuntimeConfig:
    api_key: str
    user_id: str
    workspace_root: str

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        key = os.environ.get("INSFORGE_API_KEY", "")
        uid = os.environ.get("SURYA_USER_ID", "anonymous")
        ws  = os.environ.get("SURYA_WORKSPACE_ROOT", os.getcwd())
        return cls(api_key=key, user_id=uid, workspace_root=ws)
