import re
from bs4 import BeautifulSoup, Comment

class HTMLCleaner:
    """Strips noise (scripts, styles, nav, headers, comments) from raw HTML and converts to clean visible text."""

    def clean(self, raw_html: str) -> str:
        if not raw_html or not raw_html.strip():
            return ""

        soup = BeautifulSoup(raw_html, "lxml")

        # 1. Decompose non-content tags
        for tag in soup(["script", "style", "noscript", "meta", "head", "footer", "nav", "svg", "iframe"]):
            tag.decompose()

        # 2. Extract and remove HTML comments
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

        # 3. Extract text while preserving structural block breaks
        text = soup.get_text(separator="\n", strip=True)

        # 4. Collapse multi-newline whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def chunk(self, text: str, max_chars: int = 12000) -> list[str]:
        """Split cleaned text into chunks safely below token limits."""
        if not text:
            return []

        if len(text) <= max_chars:
            return [text]

        chunks = []
        remaining = text
        while len(remaining) > max_chars:
            split_at = remaining.rfind("\n", 0, max_chars)
            if split_at == -1 or split_at < (max_chars // 2):
                split_at = max_chars

            chunk_content = remaining[:split_at].strip()
            if chunk_content:
                chunks.append(chunk_content)
            remaining = remaining[split_at:].lstrip()

        if remaining.strip():
            chunks.append(remaining.strip())

        return chunks
