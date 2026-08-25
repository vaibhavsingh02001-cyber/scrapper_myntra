import os
import aiofiles
from typing import Dict, Any, Optional
from backend.engines.bs4_engine import BS4Engine
from backend.engines.playwright_engine import PlaywrightEngine
from backend.engines.detector import detect_mode
from backend.engines.html_cleaner import HTMLCleaner
from backend.config import settings

class ScraperService:
    """Orchestrates web scraping across static, dynamic, and fallback engines."""

    def __init__(self):
        self.bs4 = BS4Engine()
        self.playwright = PlaywrightEngine()
        self.cleaner = HTMLCleaner()

    async def scrape(self, url: str, mode: str = "auto", options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main scrape entry point.
        Returns dict:
          {
            "raw_html": str,
            "cleaned_text": str,
            "chunks": list[str],
            "mode_used": str
          }
        """
        options = options or {}
        resolved_mode = await detect_mode(url, mode)

        try:
            if resolved_mode == "playwright":
                raw_html, cleaned = await self.playwright.fetch(
                    url, wait_for_selector=options.get("wait_for_selector")
                )
            else:
                raw_html, cleaned = await self.bs4.fetch(url)

            # Heuristic fallback: If static cleaning yields near-empty text, try Playwright
            if resolved_mode == "beautifulsoup" and len(cleaned) < 200:
                try:
                    raw_html, cleaned = await self.playwright.fetch(url)
                    resolved_mode = "playwright_fallback"
                except Exception:
                    pass

        except Exception as e:
            # Fallback strategy: if Playwright failed, try BS4 as secondary option
            if resolved_mode == "playwright":
                try:
                    raw_html, cleaned = await self.bs4.fetch(url)
                    resolved_mode = "beautifulsoup_fallback"
                except Exception:
                    raise e
            else:
                raise e

        # Chunk cleaned text safely for Groq LLM token limits
        max_chars = settings.MAX_TOKENS_PER_CHUNK * 4
        chunks = self.cleaner.chunk(cleaned, max_chars=max_chars)

        return {
            "raw_html": raw_html,
            "cleaned_text": cleaned,
            "chunks": chunks,
            "mode_used": resolved_mode
        }

    async def save_raw_html(self, job_id: str, raw_html: str) -> str:
        """Saves raw HTML snapshot to storage path."""
        storage_dir = os.path.join(settings.STORAGE_PATH, "raw")
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, f"{job_id}.html")

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(raw_html or "")

        return file_path
