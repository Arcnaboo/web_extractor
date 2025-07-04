#!/usr/bin/env python3
"""
data_gathering_web_crawler.py - Written by Arda Akgur

Recursively crawls web pages starting from a given URL.
Uses GroqHelper to classify content as worth saving.
Saves only save-worthy text to disk.
"""

import sys
import os
import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from groq_helper import GroqHelper  # assumes your GroqHelper class is saved in groq_helper.py

class DataGatheringCrawler:
    def __init__(self, start_url, master, groq_helper):
        self.url = start_url
        self.master = master
        self.groq = groq_helper

    async def crawl(self):
        print(f"[+] Crawling: {self.url}")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(self.url)
                resp.raise_for_status()
                html = resp.text
        except Exception as e:
            print(f"[!] Failed to fetch {self.url}: {e}")
            return

        soup = BeautifulSoup(html, "html.parser")
        text = self.extract_text(soup)
        
        if text:
            save = await self.groq.is_save_worthy(text)
            if save:
                self.save_content(text)

        for a in soup.find_all("a", href=True):
            link = urljoin(self.url, a["href"])
            if urlparse(link).scheme in ("http", "https"):
                if self.master.should_visit(link):
                    crawler = DataGatheringCrawler(link, self.master, self.groq)
                    self.master.add_task(crawler.crawl())

    def extract_text(self, soup):
        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return text if len(text) > 100 else None  # skip trivial content

    def save_content(self, text):
        filename = f"page_{len(self.master.visited)}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {self.url}\n\n{text}\n")
        print(f"[✓] Saved relevant content: {filename}")

class MasterCrawler:
    def __init__(self):
        self.visited = set()
        self.tasks = []

    def should_visit(self, url):
        if url not in self.visited:
            self.visited.add(url)
            return True
        return False

    def add_task(self, coro):
        self.tasks.append(asyncio.create_task(coro))

    async def run(self, start_url, groq_helper):
        self.should_visit(start_url)
        crawler = DataGatheringCrawler(start_url, self, groq_helper)
        self.add_task(crawler.crawl())
        await asyncio.gather(*self.tasks)

async def main():
    if len(sys.argv) != 2:
        print("Usage: python data_gathering_web_crawler.py <start_url>")
        sys.exit(1)

    start_url = sys.argv[1]
    groq_helper = GroqHelper()
    master = MasterCrawler()
    await master.run(start_url, groq_helper)

    print("\n[✓] Crawl completed.")
    print(f"[+] Total unique pages visited: {len(master.visited)}")

if __name__ == "__main__":
    asyncio.run(main())
