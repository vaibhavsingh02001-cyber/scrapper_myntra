import pytest
import os
import shutil
from backend.engines.html_cleaner import HTMLCleaner
from backend.engines.detector import detect_mode
from backend.services.scraper_service import ScraperService

def test_html_cleaner_removes_scripts_and_styles():
    cleaner = HTMLCleaner()
    raw_html = """
    <html>
        <head><title>Test Page</title><style>body { color: red; }</style></head>
        <body>
            <script>alert("xss");</script>
            <nav><a href="#">Nav Link</a></nav>
            <h1>Main Title</h1>
            <p>This is a test paragraph.</p>
            <footer>Footer Info</footer>
        </body>
    </html>
    """
    cleaned = cleaner.clean(raw_html)

    assert "alert" not in cleaned
    assert "color: red" not in cleaned
    assert "Nav Link" not in cleaned
    assert "Footer Info" not in cleaned
    assert "Main Title" in cleaned
    assert "This is a test paragraph." in cleaned

def test_html_cleaner_chunking():
    cleaner = HTMLCleaner()
    large_text = "Line content item.\n" * 1000  # ~19,000 chars

    chunks = cleaner.chunk(large_text, max_chars=5000)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 5100  # Margin allowance

@pytest.mark.asyncio
async def test_detect_mode_static_and_dynamic():
    mode_static = await detect_mode("https://example.com", mode="static")
    assert mode_static == "beautifulsoup"

    mode_dynamic = await detect_mode("https://example.com", mode="dynamic")
    assert mode_dynamic == "playwright"

@pytest.mark.asyncio
async def test_save_raw_html(tmp_path):
    service = ScraperService()
    test_html = "<html><body><h1>Hello World</h1></body></html>"
    job_id = "test-job-123"

    saved_path = await service.save_raw_html(job_id, test_html)
    assert os.path.exists(saved_path)

    with open(saved_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == test_html

    # Cleanup temp file
    if os.path.exists(saved_path):
        os.remove(saved_path)
