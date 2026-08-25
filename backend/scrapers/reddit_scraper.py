from typing import List, Dict, Any, Optional
import os

# Target subreddits and search keywords for Myntra fashion wishlist research
REDDIT_SUBREDDITS = [
    "IndianFashionAddicts",
    "IndianSkincareAddicts",
    "india",
    "femalefashionadvice",
    "FashionAdvice",
    "AskIndia"
]

REDDIT_SEARCH_QUERIES = [
    "Myntra wishlist",
    "Myntra still deciding",
    "Myntra size chart",
    "Myntra returned it",
    "Myntra saved for later",
    "Myntra waiting for price drop",
    "Myntra purchase",
    "Myntra return",
    "Myntra size fit",
    "Myntra delivery quality",
]

class RedditScraper:
    """Scrapes Reddit posts and comments mentioning Myntra/AJIO fashion discussions."""

    def __init__(self, max_posts: int = 500):
        self.max_posts = max_posts
        self._praw_client = None

    def _get_client(self):
        """Lazy-initializes PRAW client from environment variables."""
        if self._praw_client is not None:
            return self._praw_client

        client_id = os.getenv("REDDIT_CLIENT_ID", "")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        user_agent = os.getenv("REDDIT_USER_AGENT", "MyntraDiscoveryEngine/1.0")

        if not client_id or not client_secret:
            raise EnvironmentError(
                "Reddit PRAW credentials not configured. "
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
            )

        import praw
        self._praw_client = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        return self._praw_client

    def collect(self) -> List[Dict[str, Any]]:
        """
        Collects Reddit posts & comments mentioning Myntra/AJIO.
        Returns list of raw review-like dicts.
        Falls back gracefully if PRAW credentials are not configured.
        """
        try:
            reddit = self._get_client()
        except EnvironmentError as e:
            print(f"[Reddit] Skipping Reddit collection: {e}")
            return []

        collected = []
        seen_ids = set()

        try:
            for query in REDDIT_SEARCH_QUERIES:
                for subreddit_name in REDDIT_SUBREDDITS:
                    try:
                        subreddit = reddit.subreddit(subreddit_name)
                        for post in subreddit.search(query, limit=20, time_filter="all"):
                            if post.id in seen_ids:
                                continue
                            seen_ids.add(post.id)

                            if post.selftext and len(post.selftext) > 30:
                                collected.append({
                                    "platform": "reddit",
                                    "app_id": None,
                                    "app_name": "Myntra/AJIO",
                                    "review_id": post.id,
                                    "review_text": f"{post.title}. {post.selftext}"[:2000],
                                    "rating": None,
                                    "author": str(post.author) if post.author else "unknown",
                                    "review_date": None
                                })

                            # Collect top comments
                            post.comments.replace_more(limit=0)
                            for comment in post.comments.list()[:5]:
                                if hasattr(comment, "body") and len(comment.body) > 30:
                                    cid = f"{post.id}_{comment.id}"
                                    if cid not in seen_ids:
                                        seen_ids.add(cid)
                                        collected.append({
                                            "platform": "reddit",
                                            "app_id": None,
                                            "app_name": "Myntra/AJIO",
                                            "review_id": cid,
                                            "review_text": comment.body[:2000],
                                            "rating": None,
                                            "author": str(comment.author) if comment.author else "unknown",
                                            "review_date": None
                                        })

                    except Exception as sub_e:
                        print(f"[Reddit] Error in r/{subreddit_name}: {sub_e}")

                if len(collected) >= self.max_posts:
                    break

        except Exception as e:
            print(f"[Reddit] Collection error: {e}")

        print(f"[Reddit] Total {len(collected)} posts/comments collected.")
        return collected[:self.max_posts]
