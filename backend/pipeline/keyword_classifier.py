import re
from typing import Dict, Any, List, Set

# ─────────────────────────────────────────────────────────────────────────────
# MYNTRA & AJIO 5-DIMENSION WISHLIST-TO-PURCHASE RESEARCH TAXONOMY
# ─────────────────────────────────────────────────────────────────────────────

TAXONOMY: Dict[str, Dict[str, Dict[str, Any]]] = {
    "wishlist_trigger": {
        "price_wait": {
            "label": "Price Wait / Sale Waiting",
            "patterns": [
                r"\bwait(?:ing)? for (?:a )?(?:sale|price drop|discount)\b",
                r"\bprice (?:too high|drop|alert)\b",
                r"\bwill buy (?:when|if) (?:price|discount)\b",
                r"\btoo expensive right now\b",
                r"\bsaved? (?:for|until) sale\b",
            ]
        },
        "styling_inspiration": {
            "label": "Styling Inspiration / Lookbook",
            "patterns": [
                r"\bstyling (?:idea|inspiration)\b",
                r"\blooks? (?:cute|aesthetic|nice|stylish|great|pretty)\b",
                r"\boutfit idea\b",
                r"\binspiration\b",
                r"\bsaw on (?:instagram|reel|influencer)\b",
            ]
        },
        "bookmark_later": {
            "label": "Bookmark for Later",
            "patterns": [
                r"\bwishlist(?:ed|ing)?\b",
                r"\bsaved? for later\b",
                r"\bbookmark(?:ed|ing)?\b",
                r"\bkeep(?:ing)? in wishlist\b",
                r"\badd(?:ed)? to (?:wishlist|list)\b",
                r"\bjust (?:saving|bookmarking)\b",
            ]
        },
        "gifting": {
            "label": "Gifting",
            "patterns": [
                r"\bgift(?:ing|ed)? (?:for|to)\b",
                r"\bbuying for (?:my|a) (?:friend|sister|brother|mother|mom|dad|husband|wife|gf|bf)\b",
                r"\bbirthday gift\b",
                r"\banniversary gift\b",
                r"\bpresent for\b",
            ]
        },
        "comparison_shopping": {
            "label": "Comparison Shopping",
            "patterns": [
                r"\bcomparing (?:options|items|dresses|tops|prices)\b",
                r"\bshortlisted\b",
                r"\bdeciding between\b",
                r"\boptions to choose from\b",
                r"\bsaved (?:a few|multiple) (?:options|items)\b",
            ]
        }
    },

    "purchase_blocker": {
        "fit_size_uncertainty": {
            "label": "Fit & Size Uncertainty",
            "patterns": [
                r"\bsize (?:chart|guide|wrong|incorrect|confusing|misleading)\b",
                r"\bwrong size\b",
                r"\brunning (?:small|large|big)\b",
                r"\bfit (?:issue|problem|not as expected|didn't fit|doesn't fit)\b",
                r"\btoo (?:small|large|big|tight|loose)\b",
                r"\bnot true to size\b",
                r"\bsizing (?:issue|confusing|inconsistent)\b",
                r"\buncertain about size\b",
                r"\bafraid it won't fit\b",
            ]
        },
        "price_timing": {
            "label": "Price Timing & Value Hesitation",
            "patterns": [
                r"\boverpriced\b",
                r"\bnot worth (?:the price|it)\b",
                r"\bprice is (?:too high|steep)\b",
                r"\bwaiting for (?:price drop|better discount)\b",
                r"\bhoping for sale\b",
                r"\bexpensive\b",
            ]
        },
        "trust_reviews_photos": {
            "label": "Trust in Reviews & Photos",
            "patterns": [
                r"\bcolor (?:looks different|not as shown|faded)\b",
                r"\bphoto vs reality\b",
                r"\bmaterial (?:looks cheap|thin|poor|different)\b",
                r"\bfake (?:review|product|image)\b",
                r"\bmisleading (?:picture|photo|image)\b",
                r"\bno photo review\b",
                r"\bdon't trust reviews\b",
                r"\bdifferent from picture\b",
            ]
        },
        "occasion_mismatch": {
            "label": "Occasion Mismatch / No Immediate Need",
            "patterns": [
                r"\bno occasion to wear\b",
                r"\bwhere (?:will|can) I wear\b",
                r"\bdon't need it right now\b",
                r"\bno specific event\b",
                r"\bjust browsing\b",
                r"\bimpulse saved\b",
            ]
        },
        "styling_doubt": {
            "label": "Styling & Wearability Doubt",
            "patterns": [
                r"\bhow to style\b",
                r"\bnot sure if it suits me\b",
                r"\bdon't know what to wear with\b",
                r"\bwill it look good\b",
                r"\bhard to pair\b",
                r"\bstyle uncertainty\b",
            ]
        },
        "competitor_comparison": {
            "label": "Competitor Comparison",
            "patterns": [
                r"\bcheaper on (?:amazon|flipkart|meesho|nykaa|zara|hm|ajio)\b",
                r"\bbetter quality on\b",
                r"\bchecking other apps\b",
                r"\bfound on (?:amazon|meesho|ajio)\b",
                r"\bprice on other site\b",
            ]
        },
        "needs_social_validation": {
            "label": "Needs Social Validation",
            "patterns": [
                r"\basked (?:my )?(?:friends|sister|mom)\b",
                r"\bshould I buy\b",
                r"\bhelp me choose\b",
                r"\bopinion on this\b",
                r"\bthoughts on this dress\b",
                r"\bvalidation\b",
            ]
        }
    },

    "intent_strength": {
        "explicit_intent": {
            "label": "Explicit Purchase Intent",
            "patterns": [
                r"\bdefinitely (?:buying|purchasing|ordering)\b",
                r"\bwill buy (?:soon|when|as soon as)\b",
                r"\bready to buy\b",
                r"\bplanning to buy\b",
                r"\bgoing to order\b",
                r"\bjust waiting for\b",
                r"\bin my cart ready\b",
            ]
        },
        "vague_passive": {
            "label": "Vague / Passive Bookmarking",
            "patterns": [
                r"\bjust (?:saved|wishlisted|looking)\b",
                r"\bmaybe (?:someday|later)\b",
                r"\bno plan to buy\b",
                r"\bjust for fun\b",
                r"\brandomly added\b",
                r"\bwindow shopping\b",
            ]
        }
    },

    "comparison_behavior": {
        "cross_platform_price": {
            "label": "Cross-Platform Price Check",
            "patterns": [
                r"\bcompare(?:d|ing)? price[s]?\b",
                r"\bchecking (?:amazon|flipkart|meesho|nykaa|zara|ajio)\b",
                r"\bcheaper on\b",
                r"\bprice difference\b",
                r"\bprice match\b",
            ]
        },
        "cross_brand": {
            "label": "Cross-Brand Comparison",
            "patterns": [
                r"\bcomparing (?:brands|labels|material)\b",
                r"\bvs (?:roadster|hrx|dressberry|anouk|libas)\b",
                r"\bwhich brand is better\b",
                r"\bbrand comparison\b",
            ]
        },
        "seeking_outside_opinion": {
            "label": "Seeking Outside Opinion (YouTube/Reddit)",
            "patterns": [
                r"\bcheck(?:ed|ing)? (?:on )?youtube\b",
                r"\byoutube (?:haul|review|video)\b",
                r"\basked on reddit\b",
                r"\breddit review\b",
                r"\binstagram review\b",
                r"\bquora review\b",
                r"\bword of mouth\b",
            ]
        }
    },

    "segment_cue": {
        "first_time_buyer": {
            "label": "First-Time Buyer",
            "patterns": [
                r"\bfirst time (?:ordering|buying|on myntra)\b",
                r"\bnew to myntra\b",
                r"\bfirst order\b",
                r"\bnever bought from\b",
            ]
        },
        "repeat_shopper": {
            "label": "Repeat Shopper / Insider",
            "patterns": [
                r"\bmyntra insider\b",
                r"\balways buy from myntra\b",
                r"\bregular customer\b",
                r"\bmy 10th order\b",
                r"\bfrequent shopper\b",
            ]
        },
        "budget_conscious": {
            "label": "Budget-Conscious",
            "patterns": [
                r"\bon a budget\b",
                r"\bbudget (?:friendly|buy)\b",
                r"\bunder (?:500|1000|1500|2000)\b",
                r"\baffordable option\b",
                r"\bstudent budget\b",
                r"\bcannot afford\b",
            ]
        },
        "occasion_driven": {
            "label": "Occasion-Driven Buyer",
            "patterns": [
                r"\bwedding (?:shopping|outfit|season)\b",
                r"\bfestival (?:wear|outfit|diwali)\b",
                r"\bcollege re-opening\b",
                r"\boffice wear\b",
                r"\bvacation outfit\b",
                r"\bparty dress\b",
            ]
        }
    }
}

class KeywordClassifier:
    """
    Classifies Myntra & AJIO review texts into the 5-dimension research taxonomy using regex patterns.
    """

    def __init__(self):
        self._compiled: Dict[str, Dict[str, List]] = {}
        for dim, labels in TAXONOMY.items():
            self._compiled[dim] = {}
            for label_key, label_data in labels.items():
                self._compiled[dim][label_key] = [
                    re.compile(pat, re.IGNORECASE) for pat in label_data["patterns"]
                ]

    def classify_text(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {dim: [] for dim in TAXONOMY}

        results = {}
        text_lower = text.lower()

        for dim, labels in self._compiled.items():
            matched_labels = []
            for label_key, compiled_patterns in labels.items():
                for pattern in compiled_patterns:
                    if pattern.search(text_lower):
                        matched_labels.append(label_key)
                        break
            results[dim] = matched_labels

        return results

    def classify_batch(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for review in reviews:
            text = review.get("review_text", "")
            review["taxonomy_tags"] = self.classify_text(text)
        return reviews

    def get_taxonomy_metadata(self) -> Dict[str, Any]:
        meta = {}
        for dim, labels in TAXONOMY.items():
            meta[dim] = {
                k: {"label": v["label"]} for k, v in labels.items()
            }
        return meta

THEMES = TAXONOMY
