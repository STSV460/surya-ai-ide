"""5-hour rolling usage window quota (Claude Code / Codex style)."""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional
import httpx

from .config import (
    INSFORGE_GATEWAY_BASE, INSFORGE_PROJECT_ID, MODEL_POINT_COST,
    QUOTA_WINDOW_SECONDS, TIER_LIMITS,
)


class QuotaExceeded(Exception):
    def __init__(self, used: float, limit: float, resets_in: float):
        self.used = used
        self.limit = limit
        self.resets_in = resets_in
        super().__init__(
            f"QUOTA_EXCEEDED used={used:.1f} limit={limit:.1f} resets_in={resets_in:.0f}s"
        )


@dataclass
class QuotaState:
    user_id: str
    tier: str
    window_start: float
    points_used: float
    bypass: bool = False

    @property
    def limit(self) -> float:
        return float(TIER_LIMITS.get(self.tier, TIER_LIMITS["free"]))

    @property
    def resets_in(self) -> float:
        return max(0.0, (self.window_start + QUOTA_WINDOW_SECONDS) - time.time())


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    per_k = MODEL_POINT_COST.get(model, 2.0)
    return per_k * (input_tokens / 2000.0 + output_tokens / 1000.0)


class QuotaClient:
    """Persists quota state in InsForge DB table `user_quota`.

    Schema:
      user_id text primary key
      tier text not null default 'free'
      window_start double precision not null
      points_used double precision not null default 0
      bypass boolean not null default false
    """

    def __init__(self, api_key: str):
        self._client = httpx.Client(
            base_url=f"https://api.insforge.dev/v1/projects/{INSFORGE_PROJECT_ID}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0,
        )

    def _fetch(self, user_id: str) -> QuotaState:
        r = self._client.get(f"/database/tables/user_quota/records/{user_id}")
        now = time.time()
        if r.status_code == 404:
            state = QuotaState(user_id, "free", now, 0.0, False)
            self._client.post(
                "/database/tables/user_quota/records",
                json={"user_id": user_id, "tier": "free",
                      "window_start": now, "points_used": 0.0, "bypass": False},
            )
            return state
        r.raise_for_status()
        row = r.json()
        state = QuotaState(
            user_id=row["user_id"], tier=row.get("tier", "free"),
            window_start=float(row.get("window_start", now)),
            points_used=float(row.get("points_used", 0.0)),
            bypass=bool(row.get("bypass", False)),
        )
        if now - state.window_start >= QUOTA_WINDOW_SECONDS:
            state.window_start = now
            state.points_used = 0.0
            self._save(state)
        return state

    def _save(self, s: QuotaState) -> None:
        self._client.patch(
            f"/database/tables/user_quota/records/{s.user_id}",
            json={"tier": s.tier, "window_start": s.window_start,
                  "points_used": s.points_used, "bypass": s.bypass},
        )

    def check(self, user_id: str, model: str,
              input_tokens: int, expected_output_tokens: int = 1000) -> QuotaState:
        s = self._fetch(user_id)
        if s.bypass:
            return s
        cost = _estimate_cost(model, input_tokens, expected_output_tokens)
        if s.points_used + cost > s.limit:
            raise QuotaExceeded(s.points_used, s.limit, s.resets_in)
        return s

    def commit(self, user_id: str, model: str,
               input_tokens: int, output_tokens: int) -> QuotaState:
        s = self._fetch(user_id)
        if s.bypass:
            return s
        s.points_used += _estimate_cost(model, input_tokens, output_tokens)
        self._save(s)
        return s

    def status(self, user_id: str) -> QuotaState:
        return self._fetch(user_id)
