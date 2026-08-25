from typing import List, Dict, Any
from app_store_scraper import AppStore

# Target apps on Apple App Store (Indian region)
APP_STORE_TARGETS = {
    "myntra": {"app_name": "Myntra", "app_id": "907394059"}
}

class AppStoreScraper:
    """Scrapes Apple App Store reviews for Myntra and AJIO."""

    def __init__(self, max_reviews_per_app: int = 5000):
        self.max_reviews = max_reviews_per_app

    def collect(self, app_name: str) -> List[Dict[str, Any]]:
        """
        Collects reviews for a given app from Apple App Store (India region).
        Returns list of raw review dicts.
        """
        target = APP_STORE_TARGETS.get(app_name.lower())
        if not target:
            raise ValueError(f"Unknown app '{app_name}'. Available: {list(APP_STORE_TARGETS.keys())}")

        print(f"[AppStore] Collecting reviews for {app_name}...")

        try:
            app = AppStore(
                country="in",
                app_name=target["app_name"],
                app_id=target["app_id"]
            )
            app.review(how_many=self.max_reviews)
            raw_reviews = app.reviews

        except Exception as e:
            print(f"[AppStore] Error collecting {app_name}: {e}")
            return []

        formatted = []
        for r in raw_reviews:
            text = r.get("review", "")
            if not text:
                continue
            formatted.append({
                "platform": "app_store",
                "app_id": target["app_id"],
                "app_name": target["app_name"],
                "review_id": str(r.get("isEdited", "")) + str(hash(text)),
                "review_text": text,
                "rating": float(r.get("rating", 0)),
                "author": r.get("userName", ""),
                "review_date": r.get("date")
            })

        print(f"[AppStore] {app_name}: Total {len(formatted)} reviews collected.")
        return formatted
