import httpx
from backend.engines.html_cleaner import HTMLCleaner
from backend.config import settings

class BS4Engine:
    """Static HTTP fetching engine using httpx and BeautifulSoup."""

    def __init__(self):
        self.cleaner = HTMLCleaner()

    async def fetch(self, url: str) -> tuple[str, str]:
        """
        Fetches static HTML from a URL.
        Returns tuple of (raw_html, cleaned_text).
        Raises httpx.HTTPError on network/HTTP failures.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            follow_redirects=True,
            verify=True
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # Verify Content-Type
            content_type = response.headers.get("content-type", "").lower()
            if content_type and "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                raise ValueError(f"URL returned non-HTML content type: {content_type}")

            raw_html = response.text
            cleaned = self.cleaner.clean(raw_html)
            return raw_html, cleaned
