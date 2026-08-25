from fastapi import APIRouter, status
from typing import Dict, Any, List
from backend.pipeline.artifact_service import ArtifactService
from backend.pipeline.keyword_classifier import TAXONOMY

router = APIRouter()

BLOCKER_TO_QUESTIONS = {
    "fit_size_uncertainty": [2, 3, 7],
    "price_timing": [1, 4, 7],
    "trust_reviews_photos": [3, 7],
    "occasion_mismatch": [4, 7],
    "styling_doubt": [7],
    "competitor_comparison": [5, 6, 7],
    "needs_social_validation": [6, 7, 9]
}

@router.get("/opportunity-map", status_code=status.HTTP_200_OK)
def get_opportunity_map_report():
    """
    Returns the final deliverable: Ranked Opportunity Map.
    Sorted by severity score / potential impact on wishlist-to-purchase conversion.
    """
    artifact = ArtifactService()
    summary = artifact.load_themes_summary()

    if not summary or "quantification" not in summary:
        return {
            "status": "no_data",
            "message": "No analysis artifact found. Run /analyze/run first.",
            "opportunity_map": []
        }

    quant = summary.get("quantification", {})
    severity_ranking = quant.get("severity_ranking", [])
    sample_quotes = summary.get("sample_quotes", {}).get("purchase_blocker", {})
    llm_sample = artifact.load_llm_sample() or []

    opportunity_map = []
    for rank, item in enumerate(severity_ranking, 1):
        blocker_key = item["blocker_key"]
        label = item["label"]
        freq_pct = item["frequency_pct"]
        severity_score = item["severity_score"]

        # Linked research questions
        linked_questions = BLOCKER_TO_QUESTIONS.get(blocker_key, [2, 7])

        # Extract 2-3 paraphrased examples
        llm_matches = [
            r.get("paraphrased_reason") for r in llm_sample
            if r.get("blocker_type") == blocker_key and r.get("paraphrased_reason")
        ]
        examples = llm_matches[:3] if llm_matches else sample_quotes.get(blocker_key, [])[:3]

        opportunity_map.append({
            "rank": rank,
            "theme_key": blocker_key,
            "theme_label": label,
            "frequency_pct": freq_pct,
            "severity_score": severity_score,
            "linked_questions": linked_questions,
            "representative_examples": examples,
            "recommendation": f"Priority #{rank} conversion friction: Address {label.lower()} to unlock saved wishlist items."
        })

    return {
        "status": "ok",
        "total_reviews_analyzed": summary.get("total_reviews_analyzed", 0),
        "opportunity_map": opportunity_map
    }
