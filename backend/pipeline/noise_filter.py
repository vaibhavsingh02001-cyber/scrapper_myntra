import re
import hashlib
import unicodedata
from typing import Dict, Any, Optional, Tuple

# PII patterns to redact
_PII_PATTERNS = [
    (re.compile(r'\b[6-9]\d{9}\b'), "[PHONE_REDACTED]"),                           # Indian mobile numbers
    (re.compile(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}'), "[EMAIL_REDACTED]"),            # Emails
    (re.compile(r'\+91[-\s]?\d{10}'), "[PHONE_REDACTED]"),                         # +91 format
    (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), "[CARD_REDACTED]"), # Card numbers
]

# Minimum quality thresholds
MIN_REVIEW_LENGTH = 30
MAX_EMOJI_RATIO = 0.6  # If >60% of chars are emoji, drop it

def _is_mostly_emoji(text: str) -> bool:
    """Returns True if more than MAX_EMOJI_RATIO of characters are emoji/symbols."""
    if not text:
        return True
    emoji_count = sum(
        1 for ch in text
        if unicodedata.category(ch) in ("So", "Sm", "Sc") or ord(ch) > 0x1F300
    )
    return (emoji_count / max(len(text), 1)) > MAX_EMOJI_RATIO

def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()[:16]

class NoiseFilter:
    """
    Applies noise filtering to raw reviews:
    - PII redaction
    - Minimum length enforcement
    - Emoji-only review drops
    - Hash-based deduplication
    """

    def __init__(self):
        self._seen_hashes: set = set()

    def reset(self):
        """Clears deduplication state for a new pipeline run."""
        self._seen_hashes = set()

    def process(self, review: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Processes a single review dict.
        Returns (cleaned_review_dict, "ok") or (None, reason_string).
        """
        text = review.get("review_text", "")
        if not text or not text.strip():
            return None, "empty_text"

        # Emoji-only check (before length — emoji strings are inherently short)
        if _is_mostly_emoji(text):
            return None, "emoji_only"

        # Length check
        if len(text.strip()) < MIN_REVIEW_LENGTH:
            return None, f"too_short:{len(text)}"

        # PII redaction
        cleaned_text = text
        for pattern, replacement in _PII_PATTERNS:
            cleaned_text = pattern.sub(replacement, cleaned_text)

        # Deduplication
        content_hash = _compute_hash(cleaned_text)
        if content_hash in self._seen_hashes:
            return None, "duplicate"
        self._seen_hashes.add(content_hash)

        cleaned_review = {**review, "review_text": cleaned_text, "content_hash": content_hash}
        return cleaned_review, "ok"

    def filter_batch(self, reviews: list) -> Tuple[list, Dict[str, int]]:
        """
        Processes a batch of reviews.
        Returns (accepted_reviews, stats_dict).
        """
        accepted = []
        stats = {"total": len(reviews), "accepted": 0, "dropped": 0, "reasons": {}}

        for review in reviews:
            cleaned, reason = self.process(review)
            if cleaned is not None:
                accepted.append(cleaned)
                stats["accepted"] += 1
            else:
                stats["dropped"] += 1
                stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1

        return accepted, stats
