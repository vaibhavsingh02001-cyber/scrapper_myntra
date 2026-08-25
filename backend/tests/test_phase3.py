import pytest
from unittest.mock import MagicMock, patch
from backend.services.groq_service import GroqService

def test_groq_json_parsing():
    service = GroqService()

    # Plain JSON string
    raw_plain = '{"product": "Widget", "price": "$10"}'
    parsed_plain = service._parse_json(raw_plain)
    assert parsed_plain == {"product": "Widget", "price": "$10"}

    # Markdown fenced JSON
    raw_fenced = "```json\n[{\"product\": \"Widget 1\"}, {\"product\": \"Widget 2\"}]\n```"
    parsed_fenced = service._parse_json(raw_fenced)
    assert isinstance(parsed_fenced, list)
    assert len(parsed_fenced) == 2

    # Malformed text surrounding JSON
    raw_surrounded = "Here is the extracted data:\n{\"items\": [1, 2, 3]}\nHope this helps!"
    parsed_surrounded = service._parse_json(raw_surrounded)
    assert parsed_surrounded == {"items": [1, 2, 3]}

def test_model_selection_logic():
    service = GroqService()

    short_chunk = "a" * 2000
    assert service._select_extraction_model(short_chunk) == service.query_model

    medium_chunk = "a" * 10000
    assert service._select_extraction_model(medium_chunk) == service.extraction_model

def test_prompt_building():
    service = GroqService()

    extract_prompts = service._build_extraction_prompt("Page text content", "Extract product names")
    assert len(extract_prompts) == 2
    assert extract_prompts[0]["role"] == "system"
    assert "Extract product names" in extract_prompts[1]["content"]

    query_prompts = service._build_query_prompt([{"name": "Laptop", "price": "$999"}], "What is the price?")
    assert len(query_prompts) == 2
    assert "What is the price?" in query_prompts[1]["content"]

@pytest.mark.asyncio
async def test_groq_extract_mocked():
    service = GroqService()

    mock_choice = MagicMock()
    mock_choice.message.content = '{"product": "Mock Product", "price": "$99.99"}'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 150

    with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
        data, tokens = await service.extract(["Chunk text"], "Extract product and price")
        assert data == {"product": "Mock Product", "price": "$99.99"}
        assert tokens == 150
