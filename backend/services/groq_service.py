import json
import re
from typing import Any, Dict, List, Union, Tuple
from groq import Groq, RateLimitError, APIConnectionError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.config import settings

class GroqService:
    """Service wrapper for Groq LLM Cloud API (LLaMA 3 / Mixtral LPUs)."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.extraction_model = settings.GROQ_EXTRACTION_MODEL
        self.query_model = settings.GROQ_QUERY_MODEL

    async def health_check(self) -> bool:
        """Verifies Groq API availability and key validity."""
        if not self.api_key or self.api_key == "gsk_your_groq_api_key_here":
            return False
        for model in [self.query_model, "groq/compound", "groq/compound-mini", "openai/gpt-oss-20b"]:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Ping"}],
                    max_tokens=5,
                    stream=False
                )
                if response.choices and len(response.choices) > 0:
                    return True
            except Exception:
                continue
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError))
    )

    async def extract(self, chunks: List[str], user_prompt: str) -> Tuple[Union[Dict[str, Any], List[Dict[str, Any]]], int]:
        """
        Extracts structured JSON data from page chunks using Groq LPUs.
        Returns tuple of (extracted_data, total_tokens_used).
        """
        if not chunks:
            return {"_warning": "No readable text content found on the target page."}, 0

        all_records: List[Dict[str, Any]] = []
        total_tokens = 0

        for chunk in chunks:
            model = self._select_extraction_model(chunk)
            messages = self._build_extraction_prompt(chunk, user_prompt)

            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    max_tokens=4096,
                    stream=False
                )

                if response.usage:
                    total_tokens += getattr(response.usage, "total_tokens", 0)

                raw_content = response.choices[0].message.content or "{}"
                parsed = self._parse_json(raw_content)

                if isinstance(parsed, list):
                    all_records.extend(parsed)
                elif isinstance(parsed, dict) and parsed:
                    # Check if model wrapped array in a root object key
                    array_key = next((k for k, v in parsed.items() if isinstance(v, list)), None)
                    if array_key:
                        all_records.extend(parsed[array_key])
                    else:
                        all_records.append(parsed)

            except APIError as e:
                # Fallback to smaller fast model if context window error
                if "context_length" in str(e).lower() and model != "openai/gpt-oss-20b":
                    response = self.client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        temperature=0.1,
                        response_format={"type": "json_object"},
                        max_tokens=4096,
                        stream=False
                    )
                    if response.usage:
                        total_tokens += getattr(response.usage, "total_tokens", 0)
                    parsed = self._parse_json(response.choices[0].message.content or "{}")
                    if isinstance(parsed, list):
                        all_records.extend(parsed)
                    elif isinstance(parsed, dict):
                        all_records.append(parsed)
                else:
                    raise e

        if not all_records:
            return {"_warning": "No matching data found for the given prompt on this page."}, total_tokens

        # If single object extracted across all chunks, return object; otherwise return list of records
        final_result = all_records if len(all_records) > 1 else all_records[0]
        return final_result, total_tokens

    async def query(self, data: Any, user_query: str) -> Tuple[Dict[str, Any], int]:
        """
        Executes natural language queries against extracted dataset.
        Returns tuple of (query_response_dict, total_tokens_used).
        """
        messages = self._build_query_prompt(data, user_query)
        candidate_models = [self.query_model, "groq/compound", "groq/compound-mini", "openai/gpt-oss-20b"]
        
        last_error = None
        for model in candidate_models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=2048,
                    stream=False
                )
                tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
                answer = response.choices[0].message.content or "No answer generated."

                return {
                    "answer": answer,
                    "relevant_records": data if isinstance(data, list) and len(data) <= 5 else None
                }, tokens
            except Exception as e:
                last_error = e
                continue
                
        return {
            "answer": f"Analysis based on dataset: Unable to reach Groq LLM API ({str(last_error)}).",
            "relevant_records": None
        }, 0

    async def summarize(self, page_text: str) -> Tuple[str, int]:
        """Summarizes visible page text."""
        messages = [
            {
                "role": "system",
                "content": "You are a web content summarizer. Provide a concise 3-5 sentence summary of the web page content."
            },
            {"role": "user", "content": page_text[:8000]}
        ]

        response = self.client.chat.completions.create(
            model=self.query_model,
            messages=messages,
            temperature=0.3,
            max_tokens=512,
            stream=False
        )

        tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
        summary = response.choices[0].message.content or ""
        return summary, tokens

    async def batch_classify(self, reviews: List[Dict[str, Any]], themes: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], int]:
        """
        Deep LLM classification of a batch of reviews using Groq.
        Each review is classified into 1+ of the 8 behavioral themes with nuanced sentiment.
        Returns (classified_reviews_list, total_tokens_used).
        """
        themes_desc = "\n".join([f"- {t['key']}: {t['label']} — {t['description']}" for t in themes])

        review_texts = []
        for i, r in enumerate(reviews):
            review_texts.append(f"[{i}] {r.get('review_text', '')[:300]}")
        reviews_block = "\n\n".join(review_texts)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a user research analyst specializing in Indian fashion e-commerce behavior.\n"
                    "Classify each review into one or more of these behavioral themes:\n\n"
                    f"{themes_desc}\n\n"
                    "Return a JSON array where each element has:\n"
                    "  - index: the review number (integer)\n"
                    "  - themes: list of matching theme keys (strings)\n"
                    "  - sentiment: 'positive', 'negative', or 'neutral'\n"
                    "  - key_insight: one sentence summarizing the core user behavior shown\n\n"
                    "Return ONLY the JSON array, no markdown, no explanation."
                )
            },
            {
                "role": "user",
                "content": f"Reviews to classify:\n\n{reviews_block}"
            }
        ]

        response = self.client.chat.completions.create(
            model=self.extraction_model,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=4096,
            stream=False
        )

        tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
        raw = response.choices[0].message.content or "{}"
        parsed = self._parse_json(raw)

        # Extract array from possible wrapper object
        if isinstance(parsed, dict):
            parsed = next((v for v in parsed.values() if isinstance(v, list)), [])

        classified = []
        for item in (parsed or []):
            idx = item.get("index", -1)
            if 0 <= idx < len(reviews):
                enriched = {
                    **reviews[idx],
                    "llm_themes": item.get("themes", []),
                    "llm_sentiment": item.get("sentiment", "neutral"),
                    "llm_key_insight": item.get("key_insight", "")
                }
                classified.append(enriched)

        return classified, tokens

    async def structured_classify(self, reviews: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """
        Structured LLM classification mapping to the 5-dimension research taxonomy.
        Outputs exact JSON structure per item:
        {source, date, wishlist_trigger, blocker_type, intent_strength, comparison_behavior, segment_cue, paraphrased_reason}
        """
        if not reviews:
            return [], 0

        review_items = []
        for i, r in enumerate(reviews):
            review_items.append({
                "id": i,
                "text": r.get("review_text", "")[:350],
                "platform": r.get("platform", "unknown"),
                "date": str(r.get("review_date", "2024-01-01"))
            })

        system_prompt = (
            "You are a user research analyst specializing in Myntra wishlist-to-purchase consumer behavior.\n"
            "Classify each input post/review against these exact taxonomy categories:\n"
            "- wishlist_trigger: price_wait | styling_inspiration | bookmark_later | gifting | comparison_shopping\n"
            "- blocker_type: fit_size_uncertainty | price_timing | trust_reviews_photos | occasion_mismatch | styling_doubt | competitor_comparison | needs_social_validation\n"
            "- intent_strength: explicit_intent | vague_passive\n"
            "- comparison_behavior: cross_platform_price | cross_brand | seeking_outside_opinion\n"
            "- segment_cue: first_time_buyer | repeat_shopper | budget_conscious | occasion_driven\n\n"
            "Output JSON with a top-level key 'classified_items' containing a list of objects:\n"
            "{\n"
            '  "classified_items": [\n'
            "    {\n"
            '      "source": "<platform_name>",\n'
            '      "date": "<date>",\n'
            '      "wishlist_trigger": "<category_key>",\n'
            '      "blocker_type": "<category_key>",\n'
            '      "intent_strength": "<category_key>",\n'
            '      "comparison_behavior": "<category_key>",\n'
            '      "segment_cue": "<category_key>",\n'
            '      "paraphrased_reason": "<1-2 sentence paraphrased summary of user hesitation/intent>"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(review_items, indent=2)}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.extraction_model,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=4096,
                stream=False
            )

            tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
            raw = response.choices[0].message.content or "{}"
            parsed = self._parse_json(raw) or {}
            items = parsed.get("classified_items", [])
            if not isinstance(items, list):
                items = next((v for v in parsed.values() if isinstance(v, list)), [])

            enriched = []
            for idx, item in enumerate(items[:len(reviews)]):
                orig = reviews[idx]
                enriched.append({
                    "review_id": orig.get("review_id", str(idx)),
                    "raw_text": orig.get("review_text", ""),
                    "source": orig.get("platform", "unknown"),
                    "date": str(orig.get("review_date", "2024-01-01")),
                    "wishlist_trigger": item.get("wishlist_trigger", "bookmark_later"),
                    "blocker_type": item.get("blocker_type", "price_timing"),
                    "intent_strength": item.get("intent_strength", "vague_passive"),
                    "comparison_behavior": item.get("comparison_behavior", "seeking_outside_opinion"),
                    "segment_cue": item.get("segment_cue", "budget_conscious"),
                    "paraphrased_reason": item.get("paraphrased_reason", orig.get("review_text", "")[:150])
                })

            return enriched, tokens
        except Exception as e:
            print(f"[GroqService] Structured classification failed: {e}")
            return [], 0


    def _select_extraction_model(self, chunk: str) -> str:
        """Selects optimal Groq model based on text chunk length."""
        if len(chunk) > 8000:
            return self.extraction_model
        return self.query_model

    def _build_extraction_prompt(self, page_text: str, user_prompt: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are an expert web data extraction assistant.\n"
                    "Extract ONLY the fields requested by the user from the provided web content.\n"
                    "Return a JSON object or JSON array. Set null for fields not present.\n"
                    "Do NOT hallucinate. Do NOT include markdown code blocks or explanations."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Web Page Content:\n```\n{page_text}\n```\n\n"
                    f"Extraction Prompt: {user_prompt}\n\n"
                    "Return clean JSON only."
                )
            }
        ]

    def _build_query_prompt(self, data: Any, user_query: str) -> List[Dict[str, str]]:
        data_str = json.dumps(data, indent=2, default=str)[:12000]
        return [
            {
                "role": "system",
                "content": (
                    "You are a data analyst. Answer the user's question accurately and concisely based ONLY on the provided dataset.\n"
                    "If the answer cannot be determined from the dataset, state so explicitly."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Scraped Dataset:\n```json\n{data_str}\n```\n\n"
                    f"Question: {user_query}"
                )
            }
        ]

    def _parse_json(self, raw: str) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Safely parses JSON with regex extraction for markdown fenced code blocks."""
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Regex match JSON block or object/array
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass

            match_brackets = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw)
            if match_brackets:
                try:
                    return json.loads(match_brackets.group(1))
                except Exception:
                    pass
        return None
