#!/usr/bin/env python3
"""
web_extractor.py - Written by Arda Akgur

Reads keywords from words.txt, searches each keyword via Google,
visits top 5 links, and crawls each using DataGatheringCrawler with GroqHelper.
"""

import asyncio
import sys
from serpapi import GoogleSearch  # pip install google-search-results
from urllib.parse import urlparse
from groq_helper import GroqHelper
from data_gathering_web_crawler import DataGatheringCrawler, MasterCrawler

SERPAPI_KEY = "YOUR_SERPAPI_KEY"  # https://serpapi.com

async def read_keywords(filepath="words.txt") -> list:
    print(f"[+] Reading keywords from {filepath}")
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

def google_search(term):
    """Uses SerpAPI to search Google and return top 5 result URLs."""
    print(f"[+] Searching Google for: {term}")
    params = {
        "q": term,
        "api_key": SERPAPI_KEY,
        "num": 5,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    links = []
    for item in results.get("organic_results", []):
        link = item.get("link")
        if link and urlparse(link).scheme in ("http", "https"):
            print(f" -> Found link: {link}")
            links.append(link)
    return links[:5]

async def crawl_links(links, groq_helper):
    """Crawls each link with your DataGatheringCrawler."""
    master = MasterCrawler()
    for link in links:
        if master.should_visit(link):
            crawler = DataGatheringCrawler(link, master, groq_helper)
            master.add_task(crawler.crawl())
    await asyncio.gather(*master.tasks)
    print(f"[✓] Finished crawling {len(master.visited)} unique pages.")

async def main():
    keywords = await read_keywords()
    groq_helper = GroqHelper()

    for keyword in keywords:
        links = google_search(keyword)
        await crawl_links(links, groq_helper)

    print("[✓] All keywords processed.")

if __name__ == "__main__":
    if not SERPAPI_KEY:
        print("Please set your SERPAPI_KEY at the top of web_extractor.py")
        sys.exit(1)
    asyncio.run(main())
