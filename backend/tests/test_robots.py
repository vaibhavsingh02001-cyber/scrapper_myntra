import pytest
from backend.engines.detector import check_robots_txt

@pytest.mark.asyncio
async def test_check_robots_txt_allowed():
    # Invalid domain should allow fetch fallback
    allowed = await check_robots_txt("http://nonexistent-domain-12345.com/page")
    assert allowed is True
