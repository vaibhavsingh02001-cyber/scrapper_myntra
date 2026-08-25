from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from backend.pipeline.artifact_service import ArtifactService
from backend.pipeline.keyword_classifier import TAXONOMY

router = APIRouter()

RESEARCH_QUESTIONS = [
    {
        "id": 1,
        "question": "Why do users add products to their wishlist?",
        "dimension": "wishlist_trigger",
        "primary_label": "price_wait",
        "description": "Analyzes the primary intent drivers for wishlisting products."
    },
    {
        "id": 2,
        "question": "What prevents wishlisted products from being purchased?",
        "dimension": "purchase_blocker",
        "primary_label": "fit_size_uncertainty",
        "description": "Identifies top conversion blockers preventing purchase execution."
    },
    {
        "id": 3,
        "question": "What uncertainties remain after users like a product?",
        "dimension": "purchase_blocker",
        "primary_label": "trust_reviews_photos",
        "description": "Measures lack of trust in reviews, fabric, and realistic photos."
    },
    {
        "id": 4,
        "question": "What causes users to postpone a purchase?",
        "dimension": "wishlist_trigger",
        "primary_label": "price_wait",
        "description": "Quantifies sale waiting and price-timing hesitations."
    },
    {
        "id": 5,
        "question": "How do users compare multiple shortlisted products?",
        "dimension": "wishlist_trigger",
        "primary_label": "comparison_shopping",
        "description": "Examines multi-product shortlisting and option narrowing."
    },
    {
        "id": 6,
        "question": "What information do users seek outside Myntra before buying?",
        "dimension": "comparison_behavior",
        "primary_label": "seeking_outside_opinion",
        "description": "Tracks off-platform research on YouTube, Reddit, and social media."
    },
    {
        "id": 7,
        "question": "What role do fit, size, styling, price, reviews, occasion, and social validation play?",
        "dimension": "purchase_blocker",
        "primary_label": "all_blockers",
        "description": "Ranks the relative severity of all key decision factors."
    },
    {
        "id": 8,
        "question": "When is the wishlist genuine purchase intent vs. just bookmarking?",
        "dimension": "intent_strength",
        "primary_label": "explicit_intent",
        "description": "Distinguishes high-intent shoppers from passive lookbook savers."
    },
    {
        "id": 9,
        "question": "How do these behaviors differ across segments?",
        "dimension": "segment_cue",
        "primary_label": "budget_conscious",
        "description": "Breaks down purchase hesitation across user segments."
    },
    {
        "id": 10,
        "question": "What unmet needs emerge consistently across conversations?",
        "dimension": "co_occurrence",
        "primary_label": "compound_blockers",
        "description": "Highlights compound blocker combinations (e.g. size uncertainty + review distrust)."
    }
]

@router.get("/questions", status_code=status.HTTP_200_OK)
def get_research_questions_mapping():
    """
    Returns data grounded answers for all 10 research questions.
    Data is dynamically computed from active analysis artifacts.
    """
    artifact = ArtifactService()
    summary = artifact.load_themes_summary()

    if not summary or "quantification" not in summary:
        return {
            "status": "no_data",
            "message": "No analysis artifact found. Run /analyze/run first.",
            "questions": RESEARCH_QUESTIONS
        }

    quant = summary.get("quantification", {})
    dims = quant.get("dimensions", {})
    llm_sample = artifact.load_llm_sample() or []

    answers = []
    for q in RESEARCH_QUESTIONS:
        q_id = q["id"]
        dim_name = q["dimension"]

        # Fetch empirical quantitative evidence
        dim_data = dims.get(dim_name, {}) if dim_name in dims else {}

        # Fetch 2-3 paraphrased LLM examples relevant to this question
        examples = []
        if llm_sample:
            matching_llm = [
                item.get("paraphrased_reason")
                for item in llm_sample
                if item.get("paraphrased_reason")
            ]
            examples = matching_llm[:3]

        if not examples:
            sample_quotes = summary.get("sample_quotes", {}).get(dim_name, {})
            all_quotes = []
            for quotes_list in sample_quotes.values():
                all_quotes.extend(quotes_list)
            examples = all_quotes[:3]

        answers.append({
            "question_id": q_id,
            "question": q["question"],
            "description": q["description"],
            "dimension": dim_name,
            "quantitative_data": dim_data,
            "representative_paraphrased_examples": examples
        })

    return {
        "status": "ok",
        "total_reviews_analyzed": summary.get("total_reviews_analyzed", 0),
        "answers": answers
    }
