import asyncio
from typing import Optional
from playwright.async_api import async_playwright
from backend.engines.html_cleaner import HTMLCleaner
from backend.config import settings

class PlaywrightEngine:
    """Dynamic headless browser engine using Playwright Chromium."""

    def __init__(self):
        self.cleaner = HTMLCleaner()

    async def fetch(self, url: str, wait_for_selector: Optional[str] = None) -> tuple[str, str]:
        """
        Launches headless Chromium, renders JavaScript content, and returns (raw_html, cleaned_text).
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()

            try:
                # Navigate and wait until network is idle
                await page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=settings.REQUEST_TIMEOUT * 1000
                )
            except Exception:
                # Fallback to domcontentloaded if networkidle times out
                try:
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=settings.REQUEST_TIMEOUT * 1000
                    )
                except Exception as e:
                    await browser.close()
                    raise e

            # Scroll down to trigger lazy loading
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await page.wait_for_timeout(500)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            # Wait for specific selector if provided
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=5000)
                except Exception:
                    pass

            raw_html = await page.content()
            await browser.close()

            cleaned = self.cleaner.clean(raw_html)
            return raw_html, cleaned
