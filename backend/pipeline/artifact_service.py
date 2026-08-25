import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

ARTIFACTS_DIR = os.path.join("backend", "artifacts")
THEMES_SUMMARY_FILE = os.path.join(ARTIFACTS_DIR, "themes_summary.json")
LLM_SAMPLE_FILE = os.path.join(ARTIFACTS_DIR, "llm_classified_sample.json")
RAW_REVIEWS_DIR = os.path.join(ARTIFACTS_DIR, "raw_reviews")

class ArtifactService:
    """
    Manages JSON artifact files for the Discovery Engine.
    The API layer is stateless — it reads from these artifacts at runtime.
    """

    def __init__(self):
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        os.makedirs(RAW_REVIEWS_DIR, exist_ok=True)

    # ─── Themes Summary Artifact ─────────────────────────────────────────────

    def save_themes_summary(self, summary: Dict[str, Any]):
        """Writes aggregated theme stats to themes_summary.json."""
        payload = {
            **summary,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        with open(THEMES_SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"[Artifact] Saved themes_summary.json ({len(summary.get('themes', {}))} themes)")

    def load_themes_summary(self) -> Optional[Dict[str, Any]]:
        """Reads themes_summary.json, returns None if not yet generated."""
        if not os.path.exists(THEMES_SUMMARY_FILE):
            return None
        with open(THEMES_SUMMARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─── LLM Classified Sample Artifact ─────────────────────────────────────

    def save_llm_sample(self, classified_reviews: List[Dict[str, Any]]):
        """Writes or appends Groq-classified review batch to llm_classified_sample.json."""
        existing = self.load_llm_sample() or []
        existing_ids = {r.get("review_id") for r in existing}
        new_unique = [r for r in classified_reviews if r.get("review_id") not in existing_ids]
        merged = existing + new_unique

        with open(LLM_SAMPLE_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, default=str)
        print(f"[Artifact] LLM sample: {len(existing)} -> {len(merged)} reviews (+{len(new_unique)} new)")

    def load_llm_sample(self) -> Optional[List[Dict[str, Any]]]:
        """Reads llm_classified_sample.json, returns None if not yet generated."""
        if not os.path.exists(LLM_SAMPLE_FILE):
            return None
        with open(LLM_SAMPLE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─── Raw Reviews Artifact ────────────────────────────────────────────────

    def save_raw_reviews(self, platform: str, app_name: str, reviews: List[Dict[str, Any]]):
        """Saves raw collected reviews to a platform-specific JSON file."""
        platform_dir = os.path.join(RAW_REVIEWS_DIR, platform)
        os.makedirs(platform_dir, exist_ok=True)
        file_path = os.path.join(platform_dir, f"{app_name.lower()}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, default=str)
        print(f"[Artifact] Saved {len(reviews)} raw reviews -> {file_path}")

    def load_all_reviews(self) -> List[Dict[str, Any]]:
        """Loads all raw reviews from all platforms combined."""
        all_reviews = []
        if not os.path.exists(RAW_REVIEWS_DIR):
            return []
        for platform in os.listdir(RAW_REVIEWS_DIR):
            platform_path = os.path.join(RAW_REVIEWS_DIR, platform)
            if not os.path.isdir(platform_path):
                continue
            for fname in os.listdir(platform_path):
                if fname.endswith(".json"):
                    with open(os.path.join(platform_path, fname), "r", encoding="utf-8") as f:
                        all_reviews.extend(json.load(f))
        return all_reviews

    def sample_for_llm(self, reviews: List[Dict[str, Any]], sample_size: int = 100) -> List[Dict[str, Any]]:
        """Returns a random sample of reviews for LLM deep classification."""
        if len(reviews) <= sample_size:
            return reviews
        return random.sample(reviews, sample_size)

    def get_artifact_status(self) -> Dict[str, Any]:
        """Returns current state of all artifacts for the health/status endpoint."""
        themes_summary = self.load_themes_summary()
        llm_sample = self.load_llm_sample()
        all_reviews_count = len(self.load_all_reviews())

        return {
            "themes_summary_exists": themes_summary is not None,
            "themes_summary_generated_at": themes_summary.get("generated_at") if themes_summary else None,
            "total_reviews_analyzed": themes_summary.get("total_reviews_analyzed", 0) if themes_summary else 0,
            "llm_sample_exists": llm_sample is not None,
            "llm_sample_size": len(llm_sample) if llm_sample else 0,
            "raw_reviews_stored": all_reviews_count
        }
