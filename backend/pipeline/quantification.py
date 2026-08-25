from typing import List, Dict, Any, Tuple
from collections import defaultdict
import statistics
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from backend.pipeline.keyword_classifier import TAXONOMY

class QuantificationEngine:
    """
    Quantifies the tagged review corpus:
    - Frequency % per dimension label
    - Sentiment polarity per dimension label
    - Co-occurrence matrix between purchase blockers and wishlist triggers
    - Time trend per label
    - Severity score calculation
    """

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs full quantification analysis over classified reviews.
        Expects review dicts with 'taxonomy_tags' = {dim: [labels]}.
        """
        total_reviews = len(reviews)
        if total_reviews == 0:
            return {"status": "empty", "total_reviews": 0}

        # 1. Frequency and Sentiment per Dimension Label
        dim_stats: Dict[str, Dict[str, Any]] = {}
        for dim, labels_def in TAXONOMY.items():
            dim_stats[dim] = {}
            for label_key, label_meta in labels_def.items():
                matching_reviews = [
                    r for r in reviews
                    if label_key in r.get("taxonomy_tags", {}).get(dim, [])
                ]
                count = len(matching_reviews)
                freq_pct = round((count / total_reviews) * 100, 1)

                # Sentiment analysis using VADER + rating
                compound_scores = []
                for r in matching_reviews:
                    text = r.get("review_text", "")
                    v_score = self.vader.polarity_scores(text)["compound"] if text else 0
                    compound_scores.append(v_score)

                avg_sentiment = round(statistics.mean(compound_scores), 3) if compound_scores else 0.0

                pos_count = sum(1 for s in compound_scores if s >= 0.05)
                neg_count = sum(1 for s in compound_scores if s <= -0.05)
                neu_count = count - (pos_count + neg_count)

                dim_stats[dim][label_key] = {
                    "label": label_meta["label"],
                    "count": count,
                    "frequency_pct": freq_pct,
                    "avg_sentiment": avg_sentiment,
                    "sentiment_polarity": {
                        "positive": pos_count,
                        "negative": neg_count,
                        "neutral": neu_count
                    }
                }

        # 2. Co-occurrence Matrix (Blocker x Trigger & Blocker x Blocker)
        blocker_keys = list(TAXONOMY["purchase_blocker"].keys())
        co_occurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for r in reviews:
            tags = r.get("taxonomy_tags", {})
            r_blockers = tags.get("purchase_blocker", [])
            r_triggers = tags.get("wishlist_trigger", [])
            r_comparisons = tags.get("comparison_behavior", [])

            all_active = r_blockers + r_triggers + r_comparisons
            for i, label1 in enumerate(all_active):
                for label2 in all_active[i + 1:]:
                    co_occurrence[label1][label2] += 1
                    co_occurrence[label2][label1] += 1

        # Format co-occurrence as serializable dict
        co_occ_formatted = {
            k: dict(v) for k, v in co_occurrence.items()
        }

        # 3. Severity Score Calculation per Blocker
        # Severity Score = (Frequency %) * (1 + Negative Sentiment Ratio) * (1 + Co-occurrence Multiplier)
        severity_scores = []
        for label_key, stats in dim_stats["purchase_blocker"].items():
            freq = stats["frequency_pct"]
            neg_ratio = stats["sentiment_polarity"]["negative"] / max(stats["count"], 1)
            # Find total co-occurrences with other blockers
            blocker_co = sum(co_occ_formatted.get(label_key, {}).get(b, 0) for b in blocker_keys if b != label_key)
            co_multiplier = min(blocker_co / max(total_reviews, 1), 2.0)

            score = round(freq * (1.0 + neg_ratio) * (1.0 + co_multiplier), 2)
            severity_scores.append({
                "blocker_key": label_key,
                "label": stats["label"],
                "frequency_pct": freq,
                "severity_score": score,
                "negative_count": stats["sentiment_polarity"]["negative"],
                "count": stats["count"]
            })

        severity_scores.sort(key=lambda x: x["severity_score"], reverse=True)

        return {
            "total_reviews": total_reviews,
            "dimensions": dim_stats,
            "co_occurrence": co_occ_formatted,
            "severity_ranking": severity_scores
        }
