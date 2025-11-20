# author Aryaman Arora

import time, random
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

STORE_NAME = "ebay_ca"
SEARCH_TERM = input("Enter search term: ").strip()

# Define a pool of user agents to rotate through
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

HEADERS = {
    "User-Agent": random.choice(UA_POOL),
    "Accept-Language": "en-CA,en;q=0.9",
}


def build_url(search_term: str) -> str:
    base = "https://www.ebay.ca/sch/i.html?"
    return base + urlencode({"_nkw": search_term})


# Retrieve HTML content using Selenium
def get_HTML(url: str) -> str:
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    # options.add_argument("--headless=new")     # hidden browser
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    #  JS to load results
    time.sleep(4)

    # simulate scroll
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    html = driver.page_source
    driver.quit()
    return html


def parse_and_Dict(html_content: str) -> dict:
    results = {STORE_NAME: []}
    soup = BeautifulSoup(html_content, "html.parser")

    # save rendered HTML 
    with open("finalEbaySoup_rendered.html", "w", encoding="utf-8") as f:
        f.write(str(soup))

    # updated eBay selectors
    product_cards = soup.select("li.s-item, li.s-item__wrapper")

    if not product_cards:
        print("No eBay products found.")
        return {STORE_NAME: []}

    for c in product_cards:
        #name
        name_tag = c.select_one("h3.s-item__title, div.s-item__title")
        name = name_tag.get_text(strip=True) if name_tag else None

        # Price
        price_tag = c.select_one("span.s-item__price")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        #\Link
        link_tag = c.select_one("a.s-item__link")
        link = link_tag["href"] if link_tag else None

        # image
        img_tag = c.select_one("img.s-item__image-img")
        img_src = img_tag.get("src") if img_tag else None

        if name:
            results[STORE_NAME].append({
                "name": name,
                "price": price,
                "product_photo": img_src,
                "description": "No description available",
                "link": link
            })

    return results


# maain 
if __name__ == "__main__":
    search_url = build_url(SEARCH_TERM)
    html_content = get_HTML(search_url)
    item_dict = parse_and_Dict(html_content)

    products = item_dict.get(STORE_NAME, [])

    if not products:
        print("No products were extracted.")
    else:
        for product in products:
            print(
                "Name:", product["name"],
                "\nPrice:", product["price"],
                "\nLink:", product["link"],
                "\nImage:", product["product_photo"],
                "\n"
            )
