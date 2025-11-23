import json
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

## CONSTANT VARIABLES
STORE_NAME = 'staples_ca'
WEB_ADDRESS = 'https://www.staples.ca/'
SEARCH_ARG = 'search?query='
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    # 'Accept-Language': 'en-US,en;q=0.9',
    #'Accept-Encoding': 'gzip, deflate, br',
    #'Connection': 'keep-alive',
}

#def scrape_staples_selenium(product_name: str):
def search_product(product_name: str):
    # --- Chrome options ---
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={HTTP_HEADERS['User-Agent']}")
    # run headless
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    search_url = f"{WEB_ADDRESS}{SEARCH_ARG}{product_name}"
    driver.get(search_url)

    # wait for the page to load and scripts to render
    time.sleep(5)

    # scroll to mimic human behavior (helps bypass blocks)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # get the rendered HTML
    html = driver.page_source
    driver.quit()

    # --- Parse with BeautifulSoup ---
    soup = BeautifulSoup(html, "html.parser")

    results = []
    for a_tag in soup.select("a.product-link"):
        text = a_tag.get_text(separator=" ", strip=True)

        # Clean up the title
        if "Quick View" in text:
            text = text.replace("Quick View", "").strip()

        link = f"https://www.staples.ca{a_tag.get('href', '')}"

        # Try to find the price near this link (look upward or in the same container)
        card = a_tag.find_parent("div", class_="product-thumbnail")
        price_el = card.select_one("span.money.pre-money") if card else None
        price = price_el.get_text(strip=True) if price_el else "N/A"

        # extract the img src
        img_tag = card.find("img")
        img_src = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

        if text:
            results.append({
                "store": STORE_NAME,
                "name": text,
                "price": price,
                "product_photo": img_src,
                "description": "No description available",
                "link": link
            })

    return json.dumps(results)

def main():
    if len(sys.argv) > 1:
        results = search_product(sys.argv[1])
        print(results)
        return

    searching = 'y'
    while searching == 'y':
        product_desc = input("Enter the name of the product: ")
        products = search_product("laptop")
        for i, p in enumerate(products, 1):
            print("Name: " + p['title'])
            print("Price: " + p['price'])
            print("Link: " + p['link'])
            print()

        user_input = input("Perform another search? (y/n): ")
        searching = user_input[0].lower()
        while searching != 'y' and searching != 'n':
            searching = input("Perform another search? (y/n): ")

    print("Thank you for shopping at Staples!")
    # page%5D=2

if __name__ == "__main__":
    main()