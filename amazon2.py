#!/usr/bin/env python3
"""
amazon_search_scrape.py
Scrape Amazon.ca search results (e.g., https://www.amazon.ca/s?k=laptop)
Outputs CSV with: title, link, price_text, rating, reviews_count, sponsored
"""

import csv
import json
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import urlencode, urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.amazon.ca/",
    "Connection": "keep-alive",
}

@dataclass
class Result:
    title: Optional[str]
    link: Optional[str]
    price_text: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]
    sponsored: bool

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5, connect=3, read=3, backoff_factor=1.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"], raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

def build_search_url(base_or_full: str, query: Optional[str]=None, page: int=1) -> str:
    # If user gave a full URL (starts with http), just tack on page if needed.
    if base_or_full.startswith("http"):
        if page > 1:
            sep = "&" if "?" in base_or_full else "?"
            return f"{base_or_full}{sep}page={page}"
        return base_or_full
    # Otherwise, treat as base like "https://www.amazon.ca/s" with a query term
    params = {"k": query or "laptop"}
    if page > 1:
        params["page"] = page
    return f"{base_or_full}?{urlencode(params)}"

def parse_price(card: BeautifulSoup) -> Optional[str]:
    off = card.select_one("span.a-price > span.a-offscreen")
    if off and off.text.strip():
        return off.text.strip()
    whole = card.select_one("span.a-price-whole")
    frac  = card.select_one("span.a-price-fraction")
    if whole:
        return (whole.text or "").strip() + (("." + frac.text.strip()) if frac else "")
    return None

def parse_rating(text: str) -> Optional[float]:
    try:
        return float(text.split()[0])
    except Exception:
        return None

def parse_reviews_count(text: str) -> Optional[int]:
    try:
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else None
    except Exception:
        return None

def parse_results(html: str) -> List[Result]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.s-main-slot div[data-component-type='s-search-result']")
    out: List[Result] = []
    for c in cards:
        h2 = c.select_one("h2 a span")
        a  = c.select_one("h2 a")
        title = h2.text.strip() if h2 else None
        link = urljoin("https://www.amazon.ca", a["href"]) if a and a.has_attr("href") else None

        price_text = parse_price(c)

        rating_span = c.select_one("span.a-icon-alt")
        rating = parse_rating(rating_span.text.strip()) if rating_span else None

        reviews_span = c.select_one("span[aria-label*='ratings'], span[aria-label*='rating']")
        if not reviews_span:
            reviews_span = c.select_one("span.a-size-base.s-underline-text")
        reviews_count = parse_reviews_count(reviews_span.text) if reviews_span else None

        # crude sponsored flag
        sponsored = bool(c.select_one("span:contains('Sponsored')"))  # may not always work

        out.append(Result(title, link, price_text, rating, reviews_count, sponsored))
    return out

def fetch_page(session: requests.Session, url: str) -> str:
    headers = dict(DEFAULT_HEADERS)
    headers["User-Agent"] = random.choice(UA_POOL)
    time.sleep(random.uniform(0.5, 1.4))
    r = session.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for {url}")
    return r.text

def search_amazon(search_url: str, pages: int=1, limit: int=0) -> List[Result]:
    sess = make_session()
    all_results: List[Result] = []
    for p in range(1, pages+1):
        url = build_search_url(search_url, page=p)
        html = fetch_page(sess, url)
        results = parse_results(html)
        all_results.extend(results)
        if pages > 1 and p < pages:
            time.sleep(random.uniform(1.0, 2.0))
    if limit > 0:
        all_results = all_results[:limit]
    return all_results

def save_csv(rows: List[Result], path: str="results.csv") -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(Result(None,None,None,None,None,False)).keys()))
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))

if __name__ == "__main__":
    # Your link:
    SEARCH_URL = "https://www.amazon.ca/s?k=laptop"
    # Fetch first page, top 20 results
    rows = search_amazon(SEARCH_URL, pages=1, limit=20)

    # Print to console (JSON lines) and save CSV
    for r in rows:
        print(json.dumps(asdict(r), ensure_ascii=False))
    save_csv(rows, "results.csv")
    print(f"\nWrote {len(rows)} rows to results.csv")
