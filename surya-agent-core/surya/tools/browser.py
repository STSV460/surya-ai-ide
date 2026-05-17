from __future__ import annotations
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from ..config import RuntimeConfig


class _Args(BaseModel):
    url: str = Field(..., description="URL to fetch.")
    selector: str = Field("", description="Optional CSS selector to extract text from.")


class BrowserTool(BaseTool):
    name: str = "browser"
    description: str = "Open a URL with Playwright Chromium, optionally extract text by CSS selector."
    args_schema: type = _Args

    def __init__(self, cfg: RuntimeConfig):
        super().__init__()

    def _run(self, url: str, selector: str = "") -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return "ERROR: playwright not installed; run `playwright install chromium`."
        with sync_playwright() as p:
            br = p.chromium.launch(headless=True)
            page = br.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            out = page.locator(selector).inner_text() if selector else page.inner_text("body")
            br.close()
            return out[:8000]


def make_tool(cfg): return BrowserTool(cfg)
