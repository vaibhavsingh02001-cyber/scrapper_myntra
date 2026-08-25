import pytest
from backend.pipeline.noise_filter import NoiseFilter
from backend.pipeline.keyword_classifier import KeywordClassifier, TAXONOMY
from backend.pipeline.theme_analyzer import ThemeAnalyzer
from backend.pipeline.artifact_service import ArtifactService


def _make_review(text: str, rating: float = 4.0, platform: str = "google_play") -> dict:
    return {
        "platform": platform,
        "app_id": "com.myntra.android",
        "app_name": "Myntra",
        "review_id": str(hash(text)),
        "review_text": text,
        "rating": rating,
        "author": "TestUser",
        "review_date": None
    }


# ─── Noise Filter Tests ───────────────────────────────────────────────────────

class TestNoiseFilter:
    def test_rejects_empty_text(self):
        f = NoiseFilter()
        r, reason = f.process(_make_review(""))
        assert r is None
        assert reason == "empty_text"

    def test_rejects_short_text(self):
        f = NoiseFilter()
        r, reason = f.process(_make_review("ok"))
        assert r is None
        assert "too_short" in reason

    def test_rejects_emoji_only(self):
        f = NoiseFilter()
        r, reason = f.process(_make_review("👍👍👍👍👍😀🎉🔥💯🛍️"))
        assert r is None
        assert reason == "emoji_only"

    def test_deduplication(self):
        f = NoiseFilter()
        text = "I wishlisted this product but could not buy it because it was out of stock."
        review = _make_review(text)
        r1, reason1 = f.process(review)
        r2, reason2 = f.process(review)
        assert r1 is not None
        assert r2 is None
        assert reason2 == "duplicate"

    def test_pii_redaction(self):
        f = NoiseFilter()
        text = "Call me on 9876543210 for more info. Great product overall and I loved it."
        r, reason = f.process(_make_review(text))
        assert r is not None
        assert "9876543210" not in r["review_text"]
        assert "[PHONE_REDACTED]" in r["review_text"]

    def test_batch_filter(self):
        f = NoiseFilter()
        reviews = [
            _make_review("I wishlisted this product and am waiting for a sale to buy it."),
            _make_review("ok"),   # too short
            _make_review("👍👍👍👍👍👍👍👍👍"),  # emoji only
            _make_review("Myntra's return policy is terrible and I had a really bad experience returning."),
        ]
        accepted, stats = f.filter_batch(reviews)
        assert stats["accepted"] == 2
        assert stats["dropped"] == 2


# ─── Keyword Classifier Tests ─────────────────────────────────────────────────

class TestKeywordClassifier:
    def test_wishlist_intent_classified(self):
        clf = KeywordClassifier()
        res = clf.classify_text("I wishlisted this product and saved it for later.")
        assert "bookmark_later" in res["wishlist_trigger"]

    def test_purchase_blocker_classified(self):
        clf = KeywordClassifier()
        res = clf.classify_text("The price is too high, waiting for price drop.")
        assert "price_timing" in res["purchase_blocker"]

    def test_size_anxiety_classified(self):
        clf = KeywordClassifier()
        res = clf.classify_text("The size chart was wrong and the dress was running small.")
        assert "fit_size_uncertainty" in res["purchase_blocker"]

    def test_price_sensitivity_classified(self):
        clf = KeywordClassifier()
        res = clf.classify_text("Waiting for a sale to buy this. It's overpriced right now.")
        assert "price_wait" in res["wishlist_trigger"]


# ─── Theme Analyzer Tests ─────────────────────────────────────────────────────

class TestThemeAnalyzer:
    def test_analyze_produces_quantification(self):
        clf = KeywordClassifier()
        analyzer = ThemeAnalyzer()

        reviews = [
            {**_make_review("I wishlisted this for my wedding outfit."), "taxonomy_tags": clf.classify_text("I wishlisted this for my wedding outfit.")},
            {**_make_review("The price is steep, hoping for a sale."), "taxonomy_tags": clf.classify_text("The price is steep, hoping for a sale.")},
            {**_make_review("The size chart was wrong. Running small."), "taxonomy_tags": clf.classify_text("The size chart was wrong. Running small.")},
        ]

        summary = analyzer.analyze(reviews)
        assert "total_reviews_analyzed" in summary
        assert summary["total_reviews_analyzed"] == 3
        assert "quantification" in summary


# ─── Artifact Service Tests ───────────────────────────────────────────────────

def test_artifact_status_no_artifacts():
    artifact = ArtifactService()
    status = artifact.get_artifact_status()
    assert "themes_summary_exists" in status
    assert "llm_sample_exists" in status
