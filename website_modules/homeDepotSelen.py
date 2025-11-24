# author Aryaman Arora
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# Selenium imports for full JS rendering
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STORE_NAME = 'homedepot_ca'

# get  HTML with Selenium 
def get_html(url: str) -> str:

    # Setup Chrome Options
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    # run headless
    # options.add_argument("--headless=new")

    #initialize Chrome web driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # print("open browser")
        driver.get(url)

        #wait for the products to load or timeout after 15 seconds
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "article.acl-product-card, div.acl-product-card")
                )
            )
            # print("product loaded good.")
        except:
            print("Timed out/Product not found")

        #  Scroll to trigger  loading
        if "page=" in url:
            # Incremental scrolling hit trigger zones
            current_height = 0
            while True:
                current_height += 1200 
                driver.execute_script(f"window.scrollTo(0, {current_height});")
                time.sleep(1) # pause let js load new node
                
                # Check total height to see if we reached the bottom
                total_height = driver.execute_script("return document.body.scrollHeight")
                if current_height >= total_height:
                    break
        else:
            driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)

        #  Return full HTML source with loaded js content 
        return driver.page_source

    finally:
        driver.quit()

# build search URL
def build_url(searchTerm: str) -> str:
    return "https://www.homedepot.ca/search?" + urlencode({"q": searchTerm})
def next_page_url(searchTerm: str, page_num: int) -> str:
    return "https://www.homedepot.ca/search?" + urlencode({"q": searchTerm, "page": page_num})

# Parse HTML and return list
def parse_and_Dict(html_content: str) -> dict:

    results = [] 
    soup = BeautifulSoup(html_content, "lxml")

    # slect all product cards
    product_cards = soup.select(
        "article.acl-product-card, "
        "div.acl-product-card, "
        "[data-component='ProductCard']"
    )

    # No products found, return empty dict
    if not product_cards:
        return [] ####

    for c in product_cards:

        # product name
        name_tag = (
            c.select_one(".acl-product-card__title")
            or c.select_one("h2")
            or c.select_one("a.acl-product-card__title-link")
        )
        prod_name = name_tag.get_text(strip=True) if name_tag else None

        #product price
        price = (
            c.select_one(".acl-product-card__price") 
            or c.select_one("[class*='price-format']")
            or c.select_one("[itemprop='price']")
        )
        
        if price:
            # price raw text format, "$179And00Cents/ each")
            raw_price = price.get_text(strip=True)
            #filter text
            clean_price = raw_price.replace("And", ".").replace("Cents", "").replace("/ each", "").strip()
            prod_price = clean_price
            try: 
                prod_price = float(prod_price.replace("$", "").replace(",", ""))
            except ValueError:
                prod_price = "N/A"
        else:
            prod_price = "N/A"

        # product image 
        img_tag = c.select_one("img")
        img_src = None
        if img_tag:
            img_src = img_tag.get("src") or img_tag.get("data-src")


        # product Link
        link_tag = c.select_one("a.acl-product-card__title-link")
        
        # if class above not found fallback H2 tag
        if not link_tag:
            link_tag = c.select_one("h2 a")

        prod_link = None
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            if href.startswith("/"):
                prod_link = "https://www.homedepot.ca" + href
            else:
                prod_link = href

        # if valid append product to list
        if prod_name:
            results.append({"store": STORE_NAME,
                "name": prod_name,
                "price": prod_price,
                "product_photo": img_src,
                "description": "No description available",
                "link": prod_link})
            
    return results

# search products used by main_module.py to return product results to main module
def search_products(search_term: str) -> list:
    
    search_url = build_url(search_term)
    html_content = get_html(search_url)
    item_list = parse_and_Dict(html_content)
    products = item_list

    return products

def get_next_page (search_term: str, page_num: int) -> list:
    next_url = next_page_url(search_term, page_num)
    html_content = get_html(next_url)
    item_list = parse_and_Dict(html_content)
    products = item_list

    return products

# Main to run as script
if __name__ == "__main__":
    SEARCH_TERM = input("Enter search term: ").strip()
    # search_url = build_url(SEARCH_TERM)
    search_url = next_page_url(SEARCH_TERM,2)
    print("this is search url:", search_url)

    # selenium gets JS rendered Html
    html_content = get_html(search_url)

    # Parse and return products dict
    item_dict = parse_and_Dict(html_content)
    products = item_dict

    if not products:
        print("No products were extracted.")
    else:
        for index, product in enumerate(products, 1):
            print(f"Item {index}:")
            print(f"Name:  {product['name']}")
            print(f"Price: {product['price']}")
            print(f"Link:  {product['link']}")
            print(f"Image: {product['product_photo']}")
            print("-" * 60) # visual separator