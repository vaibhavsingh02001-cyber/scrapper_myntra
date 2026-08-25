from fastapi import APIRouter, BackgroundTasks, status
from backend.pipeline.artifact_service import ArtifactService
from backend.pipeline.keyword_classifier import KeywordClassifier, THEMES
from backend.pipeline.theme_analyzer import ThemeAnalyzer
from backend.services.groq_service import GroqService

router = APIRouter()


async def run_analysis_pipeline(use_llm: bool):
    """Background task: classifies all collected reviews and writes artifacts."""
    artifact = ArtifactService()
    keyword_clf = KeywordClassifier()
    analyzer = ThemeAnalyzer()

    print("[Analyze] Loading all collected reviews...")
    all_reviews = artifact.load_all_reviews()

    if not all_reviews:
        print("[Analyze] No reviews found. Run /collect first.")
        return

    print(f"[Analyze] Classifying {len(all_reviews)} reviews with keyword engine...")
    classified = keyword_clf.classify_batch(all_reviews)

    # Generate theme summary artifact from keyword classifier
    summary = analyzer.analyze(classified)
    artifact.save_themes_summary(summary)
    print(f"[Analyze] themes_summary.json saved ({len(summary.get('themes', {}))} themes)")

    # Optional: Groq LLM deep structured classification on a sample batch
    if use_llm:
        print("[Analyze] Running Groq LLM structured classification on 100-review sample...")
        sample = artifact.sample_for_llm(all_reviews, sample_size=100)

        try:
            groq = GroqService()
            llm_classified, tokens = await groq.structured_classify(sample)
            artifact.save_llm_sample(llm_classified)
            print(f"[Analyze] LLM structured classification complete. Tokens used: {tokens}")
        except Exception as e:
            print(f"[Analyze] Groq LLM classification failed (non-fatal): {e}")

    print("[Analyze] Analysis pipeline complete.")


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(
    background_tasks: BackgroundTasks,
    use_llm: bool = True
):
    """
    Triggers the full analysis pipeline:
    1. Keyword classification of all collected reviews → themes_summary.json
    2. Optional Groq LLM deep classification of 100-review sample → llm_classified_sample.json
    use_llm=false skips Groq (useful for testing without API key)
    """
    background_tasks.add_task(run_analysis_pipeline, use_llm=use_llm)

    return {
        "status": "running",
        "use_llm": use_llm,
        "message": "Analysis pipeline started. Check /insights/summary to see results when complete."
    }


@router.post("/keyword-only", status_code=status.HTTP_200_OK)
async def run_keyword_classification_sync():
    """
    Synchronously runs keyword classification only (no Groq).
    Returns immediate theme distribution for quick inspection.
    """
    artifact = ArtifactService()
    keyword_clf = KeywordClassifier()
    analyzer = ThemeAnalyzer()

    all_reviews = artifact.load_all_reviews()
    if not all_reviews:
        return {"status": "no_data", "message": "No reviews found. Run /collect first."}

    classified = keyword_clf.classify_batch(all_reviews)
    summary = analyzer.analyze(classified)
    artifact.save_themes_summary(summary)

    return {
        "status": "ok",
        "total_reviews": len(all_reviews),
        "total_classified": summary["total_classified"],
        "top_themes": summary["top_themes"][:5]
    }
