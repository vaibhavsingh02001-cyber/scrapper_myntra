# Scrapers package — review collection from Google Play, App Store, Reddit
from backend.scrapers.play_store_scraper import PlayStoreScraper
from backend.scrapers.app_store_scraper import AppStoreScraper
from backend.scrapers.reddit_scraper import RedditScraper

__all__ = ["PlayStoreScraper", "AppStoreScraper", "RedditScraper"]
