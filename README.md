# web_extractor

Minimal web crawler for discovering and extracting relevant knowledge from the web.

## Files

- data_gathering_web_crawler.py - Recursively crawls a page, uses GroqHelper to decide what content to save.
- groq_helper.py - Calls Groq LLM to classify page text as save-worthy.
- web_extractor.py - Reads keywords from words.txt, searches Google via SerpAPI, visits top links, and crawls them.
- LICENSE - MIT License
- README.md - This documentation.

## Requirements

Python 3.8+
Install dependencies:
pip install httpx beautifulsoup4 groq google-search-results

You need a Groq API key (GROQ_API_KEY) and a SerpAPI key (SERPAPI_KEY).

## Usage

To crawl a single website:
python data_gathering_web_crawler.py https://example.com

To crawl keywords:
- Create words.txt with one keyword per line.
- Run:
python web_extractor.py

## Notes

Be mindful of SerpAPI rate limits. Keep your API keys private.

## License

MIT License
