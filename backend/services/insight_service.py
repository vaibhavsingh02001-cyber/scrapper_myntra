from typing import Dict, Any, List, Optional
from backend.pipeline.artifact_service import ArtifactService
from backend.pipeline.theme_analyzer import ThemeAnalyzer
from backend.pipeline.keyword_classifier import THEMES

class InsightService:
    """
    Reads from artifact files to power the Discovery Pulse Dashboard.
    Stateless — all data comes from JSON artifacts.
    """

    def __init__(self):
        self.artifact = ArtifactService()
        self.analyzer = ThemeAnalyzer()

    def get_themes_overview(self) -> Dict[str, Any]:
        """Returns full theme distribution summary for the dashboard."""
        summary = self.artifact.load_themes_summary()
        if not summary:
            return {
                "status": "no_data",
                "message": "No analysis artifacts found. Run /analyze/run first.",
                "themes": {}
            }
        return {**summary, "status": "ok"}

    def get_theme_quotes(
        self,
        theme_key: str,
        limit: int = 10,
        platform: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """Returns verbatim quotes for a specific theme with optional filters."""
        if theme_key not in THEMES and theme_key != "all":
            return {"error": f"Unknown theme '{theme_key}'"}

        all_reviews = self.artifact.load_all_reviews()
        if not all_reviews:
            return {"quotes": [], "total": 0, "message": "No reviews collected yet."}

        # Load themes from the classified dataset if available, else use raw
        llm_sample = self.artifact.load_llm_sample()

        if theme_key == "all":
            # Return top quotes across all themes from LLM sample
            quotes = [
                {
                    "text": r.get("review_text", ""),
                    "themes": r.get("themes", []),
                    "rating": r.get("rating"),
                    "platform": r.get("platform"),
                    "app_name": r.get("app_name"),
                }
                for r in (llm_sample or all_reviews)
                if 50 < len(r.get("review_text", "")) < 400
            ][:limit]
        else:
            quotes = self.analyzer.get_top_quotes(
                all_reviews,
                theme_key=theme_key,
                limit=limit,
                platform=platform,
                min_rating=min_rating,
                max_rating=max_rating
            )

        return {
            "theme": theme_key,
            "theme_label": THEMES.get(theme_key, {}).get("label", theme_key),
            "quotes": quotes,
            "total_returned": len(quotes)
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns high-level stats for dashboard metric cards."""
        summary = self.artifact.load_themes_summary()
        artifact_status = self.artifact.get_artifact_status()

        if not summary:
            return {
                "status": "no_data",
                "artifact_status": artifact_status
            }

        top_themes = summary.get("top_themes", [])
        themes_data = summary.get("themes", {})

        # Dominant theme
        dominant_theme = top_themes[0] if top_themes else None
        dominant_label = themes_data.get(dominant_theme[0], {}).get("label", "") if dominant_theme else None

        return {
            "status": "ok",
            "total_reviews": summary.get("total_reviews_analyzed", 0),
            "total_classified": summary.get("total_classified", 0),
            "platform_breakdown": summary.get("platform_breakdown", {}),
            "app_breakdown": summary.get("app_breakdown", {}),
            "dominant_theme": dominant_theme[0] if dominant_theme else None,
            "dominant_theme_label": dominant_label,
            "dominant_theme_count": dominant_theme[1] if dominant_theme else 0,
            "top_5_themes": [
                {
                    "key": k,
                    "label": themes_data.get(k, {}).get("label", k),
                    "count": c,
                    "percentage": themes_data.get(k, {}).get("percentage", 0)
                }
                for k, c in top_themes
            ],
            "llm_sample_size": artifact_status.get("llm_sample_size", 0),
            "generated_at": summary.get("generated_at")
        }
