"""OpenAI-compatible client pointed at InsForge Model Gateway with 5h quota middleware."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from openai import OpenAI

from .config import INSFORGE_GATEWAY_BASE, MODEL_BY_AGENT, MODEL_MANAGER, RuntimeConfig
from .quota import QuotaClient, QuotaExceeded


class SuryaLLM:
    def __init__(self, cfg: RuntimeConfig):
        self.cfg = cfg
        self.client = OpenAI(base_url=INSFORGE_GATEWAY_BASE, api_key=cfg.api_key)
        self.quota = QuotaClient(cfg.api_key)

    def model_for(self, agent_role: str) -> str:
        return MODEL_BY_AGENT.get(agent_role, MODEL_MANAGER)

    def chat(self, agent_role: str, messages: List[Dict[str, Any]],
             expected_output_tokens: int = 1000, **kwargs) -> Dict[str, Any]:
        model = self.model_for(agent_role)
        input_tokens = sum(len(str(m.get("content", ""))) for m in messages) // 4
        self.quota.check(self.cfg.user_id, model, input_tokens, expected_output_tokens)
        resp = self.client.chat.completions.create(model=model, messages=messages, **kwargs)
        usage = getattr(resp, "usage", None)
        in_tok = getattr(usage, "prompt_tokens", input_tokens) if usage else input_tokens
        out_tok = getattr(usage, "completion_tokens", 0) if usage else 0
        self.quota.commit(self.cfg.user_id, model, in_tok, out_tok)
        return resp.model_dump() if hasattr(resp, "model_dump") else resp
