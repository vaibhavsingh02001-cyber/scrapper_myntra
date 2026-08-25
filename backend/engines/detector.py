import httpx
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

async def check_robots_txt(url: str, user_agent: str = "*") -> bool:
    """
    Checks robots.txt for the given URL domain.
    Returns True if scraping is allowed, False if disallowed.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return True

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
            resp = await client.get(robots_url)
            if resp.status_code == 200:
                rp = RobotFileParser()
                rp.parse(resp.text.splitlines())
                return rp.can_fetch(user_agent, url)
    except Exception:
        # Allow fetching if robots.txt is unreachable or missing
        pass

    return True


async def detect_mode(url: str, mode: str = "auto") -> str:
    """
    Determines whether to use 'beautifulsoup' (static) or 'playwright' (dynamic).
    Modes:
      - 'static': returns 'beautifulsoup'
      - 'dynamic': returns 'playwright'
      - 'auto': inspects initial HTML response heuristics
    """
    if mode == "static":
        return "beautifulsoup"
    if mode == "dynamic":
        return "playwright"

    # Auto-detection heuristic
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = await client.get(url, headers=headers)

            text_lower = r.text.lower()
            # If body is minimal or explicitly relies on SPA mounting / noscript
            if len(r.text) < 1500 or "<noscript>" in text_lower or 'id="root"' in text_lower or 'id="app"' in text_lower:
                return "playwright"
    except Exception:
        # On connection failure during pre-check, default to Playwright
        return "playwright"

    return "beautifulsoup"
