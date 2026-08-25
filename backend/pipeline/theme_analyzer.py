from typing import List, Dict, Any, Optional
from collections import defaultdict
from backend.pipeline.keyword_classifier import TAXONOMY
from backend.pipeline.quantification import QuantificationEngine

class ThemeAnalyzer:
    """
    Aggregates classified reviews using the 5-dimension research taxonomy & QuantificationEngine.
    """

    def __init__(self):
        self.quantifier = QuantificationEngine()

    def analyze(self, classified_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes a list of reviews containing 'taxonomy_tags'.
        Returns structured analysis & quantification data for artifact storage.
        """
        total = len(classified_reviews)

        # Run quantification engine
        quant_results = self.quantifier.analyze(classified_reviews)

        # Platform breakdown
        platform_counts: Dict[str, int] = defaultdict(int)
        for r in classified_reviews:
            platform_counts[r.get("platform", "unknown")] += 1

        # Extract sample quotes per dimension label
        dimension_quotes: Dict[str, Dict[str, List[str]]] = {}
        for dim, labels_def in TAXONOMY.items():
            dimension_quotes[dim] = {}
            for label_key in labels_def:
                matching = [
                    r.get("review_text", "") for r in classified_reviews
                    if label_key in r.get("taxonomy_tags", {}).get(dim, [])
                    and 40 < len(r.get("review_text", "")) < 400
                ]
                dimension_quotes[dim][label_key] = matching[:3]

        return {
            "total_reviews_analyzed": total,
            "platform_breakdown": dict(platform_counts),
            "quantification": quant_results,
            "sample_quotes": dimension_quotes,
            "top_blockers": quant_results.get("severity_ranking", [])[:5] if isinstance(quant_results, dict) else []
        }

    def get_top_quotes(
        self,
        classified_reviews: List[Dict[str, Any]],
        dimension: str,
        label_key: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns top verbatim quotes for a specific taxonomy dimension and label key.
        """
        matching = [
            r for r in classified_reviews
            if label_key in r.get("taxonomy_tags", {}).get(dimension, [])
            and 40 < len(r.get("review_text", "")) < 600
        ]

        return [
            {
                "text": r["review_text"],
                "rating": r.get("rating"),
                "platform": r.get("platform"),
                "author": r.get("author", "Anonymous")
            }
            for r in matching[:limit]
        ]
