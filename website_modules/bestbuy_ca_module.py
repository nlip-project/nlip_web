# author Aryaman Arora
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STORE_NAME = 'bestbuy_ca'

# get html with selenium
def get_html(url: str) -> str:
    options = Options() 
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    # fix for "Access Denied" issue
    options.add_argument("--disable-http2")
    #add user agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_argument("--headless") ######################################

    driver = webdriver.Chrome(options=options)

    try:
        #print (open brows)
        driver.get(url)
        
        # Waait product load or timeout 20 sec
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "productItemName_3IZ3c"))
            )
            # print("prods loaded")
        except:
            print("Timed out/Product not found")

        # scroll trigger product loading 
        for i in range(1, 5):
            driver.execute_script(f"window.scrollTo(0, {i * 800});")
            time.sleep(random.uniform(0.5, 1.0))
        
         #  Return full HTML source with loaded js content 
        return driver.page_source

    finally:
        driver.quit()

# function to build search url 
def build_url(searchTerm: str) -> str:
    base_url = "https://www.bestbuy.ca/en-ca/search?"
    return base_url + urlencode({"search": searchTerm})

#parse html return list
def parse_and_list(html_content: str) -> dict:
    results = []
    soup = BeautifulSoup(html_content, "lxml")

    # product name
    name_tags = soup.select(".productItemName_3IZ3c")
    if not name_tags:
        return [] ################]
    for name_tag in name_tags:
        # get name
        prod_name = name_tag.get_text(strip=True)
        card = name_tag.find_parent("li") 
        if not card: # backstep to find name if not found by .find_parent("li")
            card = name_tag.find_parent("div", class_=lambda x: x and 'col-xs' in x)
        
        if not card: #useless entry 
            continue

        #product price
        price_tag = card.select_one(".productPricingContainer_3gTS3 span[data-automation='product-price']")
        
        prod_price = "N/A"
        if price_tag:
            raw_price = price_tag.get_text(strip=True)
            # fix price duplicated eg $99$99 split 
            if raw_price.count('$') > 1:
                # split price by $ take second part
                parts = raw_price.split('$') # parts[0] is empty, parts[1] is first price
                if len(parts) > 1:
                    prod_price = "$" + parts[1]
            else:
                prod_price = raw_price
        else:
            #check price in parent container not found above
            container = card.select_one(".productPricingContainer_3gTS3")
            if container:
                raw_price = container.get_text(strip=True)
                if raw_price.count('$') > 1:
                    prod_price = raw_price.split('$')[1]
                    prod_price = float(prod_price.replace("$", "").replace(",", ""))
                else:
                    prod_price = raw_price

        # product image 
        img_src = None
        #select image with class productItemImage
        img_tag = card.find("img", class_=lambda x: x and "productItemImage" in x)
        
        # class select not work try to use thumbnail image div
        if not img_tag:
            img_tag = card.select_one("div[data-automation='product-image'] img")
            
        # first 2 options not work grab any img tag in card
        if not img_tag:
            img_tag = card.select_one("img")

        if img_tag: 
            srcset = img_tag.get("srcset")
            if srcset:
                # bestbuy use srcset with multiple URLs, extract first clean URL
                first_entry = srcset.split(",")[0] 
                img_src = first_entry.strip().split(" ")[0]
            else:
                img_src = img_tag.get("src")

        # product Link
        link_tag = card.select_one("a[itemprop='url']") or card.select_one("a")
        prod_link = None
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            if href.startswith("/"):
                prod_link = "https://www.bestbuy.ca" + href
            else:
                prod_link = href

        results.append({
                "store": STORE_NAME,
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
    products = parse_and_list(html_content)
    return json.dumps(products)

# main function for use as a script 
if __name__ == "__main__":

    SEARCH_TERM = input("Enter search term: ").strip()
    search_url = build_url(SEARCH_TERM)
    html_content = get_html(search_url)
    item_list = parse_and_list(html_content)
    products = item_list

    if not products:
        print("no products found")
    else:
        for index, product in enumerate(products, 1):
            print(f"Item {index}:")
            print(f"Name:  {product['name']}")
            print(f"Price: {product['price']}")
            print(f"Link:  {product['link']}")
            print(f"Image: {product['product_photo']}")
            print("-" * 60)