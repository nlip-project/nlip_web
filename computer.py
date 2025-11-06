# pip install playwright
# playwright install chromium
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re, csv, time

START_URL = "https://www.canadacomputers.com/en/915/desktop-graphics-cards"

def extract_products(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(
        ".product, .product-item, li.product, article, .product-list-item, .productGrid__item"
    )
    results = []

    # Fallback: anything that looks like a tile with a link + a $price
    if not cards:
        candidates = soup.select("section, div")
        cards = [c for c in candidates if c.select_one("a") and c.find(string=lambda s: s and "$" in s)]

    for card in cards:
        a = (card.select_one("a[title], .product__title a, h2 a, h3 a, .product-title a")
             or card.find("a"))
        title = (a.get("title") if a and a.has_attr("title")
                 else (a.get_text(strip=True) if a else ""))

        # Try multiple price patterns
        price_el = (card.select_one(".price, .product-price, .sale-price, .money, [data-price]")
                    or card.find(string=lambda s: s and re.search(r"\$\s*\d", s)))
        price = (price_el.get_text(strip=True) if hasattr(price_el, "get_text")
                 else (price_el.strip() if price_el else ""))

        if title and price and "$" in price:
            results.append((title, price))
    return results

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        locale="en-CA",
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
        viewport={"width": 1280, "height": 2000},
    )
    page = context.new_page()

    # 1) Visit home to set cookies, THEN category
    page.goto("https://www.canadacomputers.com/", wait_until="domcontentloaded", timeout=60000)
    # If a cookie banner shows up, accept it (best-effort; ignore if not found)
    try:
        page.get_by_role("button", name=re.compile("Accept|Agree|OK|Got it", re.I)).click(timeout=3000)
    except:
        pass

    page.goto(START_URL, wait_until="networkidle", timeout=60000)

    # Guard: if we still got bounced to Facebook, bail out
    if "facebook.com" in page.url.lower():
        raise SystemExit("They’re bouncing even real browsers on your network. Try a different network or Selenium with a real Chrome profile.")

    # Scroll to load lazy content
    for _ in range(6):
        page.mouse.wheel(0, 3000)
        time.sleep(0.4)

    html = page.content()
    products = extract_products(html)

    # Optional: follow pagination (CC uses page params; try next buttons if present)
    next_links = page.locator("a:has-text('Next'), a[rel='next']").all()
    if next_links:
        try:
            next_links[0].click(timeout=5000)
            page.wait_for_load_state("networkidle")
            for _ in range(4):
                page.mouse.wheel(0, 3000)
                time.sleep(0.3)
            products += extract_products(page.content())
        except:
            pass

    browser.close()

# Dump
for t, p in products[:15]:
    print(f"{t} — {p}")

with open("cc_gpus.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["title", "price"])
    w.writerows(products)
print(f"Saved {len(products)} items to cc_gpus.csv")
