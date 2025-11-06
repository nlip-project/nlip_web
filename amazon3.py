# mini_amazon_search_debug.py
import random, time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

SEARCH_TERM = input("Enter search term: ").strip()
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def build_url(q: str) -> str:
    return "https://www.amazon.ca/s?" + urlencode({"k": q})

def fetch_html(url: str, tries: int = 4) -> str:
    for i in range(tries):
        headers = {
            "User-Agent": random.choice(UA_POOL),
            "Accept-Language": "en-CA,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.amazon.ca/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        }
        time.sleep(random.uniform(0.7, 1.6) + i * 0.8)  # jitter + backoff
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.text
        if r.status_code in (429, 503):
            continue
        r.raise_for_status()
    raise SystemExit("Blocked (429/503). Try again or use Playwright/API.")

def parse_and_print(html: str):
    # quick CAPTCHA detect
    low = html.lower()
    if "captchachallenge" in low or "enter the characters you see below" in low:
        print("Got CAPTCHA page — slow down or try again later.")
        return

    # save for quick inspection
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "lxml")

    # BROADER: any element with a non-empty data-asin under the main slot
    cards = soup.select("div.s-main-slot [data-asin]:not([data-asin=''])")
    if not cards:
        print("No product cards found. Open debug.html to see what came back.")
        return

    for c in cards:
        # title variants
        t = (c.select_one("h2 a span")
             or c.select_one("h2 span.a-text-normal")
             or c.select_one("h2"))
        title = t.get_text(strip=True) if t else None

        # price
        p = c.select_one("span.a-price > span.a-offscreen")
        price = p.get_text(strip=True) if p else None

        # rating
        r = c.select_one("span.a-icon-alt")
        rating = None
        if r:
            parts = r.get_text(strip=True).split()
            rating = parts[0] if parts else None

        if title:
            print(f"title:   {title}")
            print(f"price:   {price or 'N/A'}")
            print(f"rating:  {rating or 'N/A'}\n")

if __name__ == "__main__":
    url = build_url(SEARCH_TERM)
    html = fetch_html(url)
    parse_and_print(html)
