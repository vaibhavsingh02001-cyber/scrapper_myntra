from typing import List, Dict, Any
from google_play_scraper import reviews, Sort, app as get_app_info
from google_play_scraper.exceptions import NotFoundError

# Target apps on Google Play
PLAY_STORE_TARGETS = {
    "myntra": "com.myntra.android"
}

class PlayStoreScraper:
    """Scrapes Google Play Store reviews for Myntra and AJIO."""

    def __init__(self, max_reviews_per_app: int = 10000):
        self.max_reviews = max_reviews_per_app

    def get_app_info(self, app_name: str) -> Dict[str, Any]:
        """Fetches app metadata from Play Store."""
        app_id = PLAY_STORE_TARGETS.get(app_name.lower())
        if not app_id:
            return {}
        try:
            info = get_app_info(app_id, lang="en", country="in")
            return {
                "app_id": app_id,
                "app_name": info.get("title", app_name),
                "score": info.get("score"),
                "ratings": info.get("ratings"),
                "reviews_count": info.get("reviews")
            }
        except Exception:
            return {"app_id": app_id, "app_name": app_name}

    def collect(self, app_name: str) -> List[Dict[str, Any]]:
        """
        Collects reviews for a given app from Google Play Store.
        Returns list of raw review dicts.
        """
        app_id = PLAY_STORE_TARGETS.get(app_name.lower())
        if not app_id:
            raise ValueError(f"Unknown app '{app_name}'. Available: {list(PLAY_STORE_TARGETS.keys())}")

        all_reviews = []
        continuation_token = None
        batch_size = 200

        print(f"[PlayStore] Collecting reviews for {app_name} ({app_id})...")

        while len(all_reviews) < self.max_reviews:
            try:
                result, continuation_token = reviews(
                    app_id,
                    lang="en",
                    country="in",
                    sort=Sort.NEWEST,
                    count=batch_size,
                    continuation_token=continuation_token
                )

                if not result:
                    break

                all_reviews.extend(result)
                print(f"[PlayStore] {app_name}: collected {len(all_reviews)} reviews so far...")

                if continuation_token is None:
                    break

            except NotFoundError:
                print(f"[PlayStore] App '{app_id}' not found.")
                break
            except Exception as e:
                print(f"[PlayStore] Error collecting {app_name}: {e}")
                break

        formatted = []
        for r in all_reviews[:self.max_reviews]:
            formatted.append({
                "platform": "google_play",
                "app_id": app_id,
                "app_name": app_name.capitalize(),
                "review_id": r.get("reviewId", ""),
                "review_text": r.get("content", ""),
                "rating": float(r.get("score", 0)),
                "author": r.get("userName", ""),
                "review_date": r.get("at")
            })

        print(f"[PlayStore] {app_name}: Total {len(formatted)} reviews collected.")
        return formatted
