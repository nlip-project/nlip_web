#author Aryaman Arora
import random, time
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlencode

STORE_NAME = 'amazon_ca'


# Define a pool of user agents to rotate through
# Used in HEADERS
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

HEADERS = {"User-Agent": random.choice(UA_POOL),
            "Accept-Language": "en-CA,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.amazon.ca/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            }

#return search url for a given search term
def build_url( searchTerm: str) -> str:
    return "https://www.amazon.ca/s?" + urlencode({"k": searchTerm})

# Retrieve HTML content from search URL
def get_HTML(url: str, tries: int = 4) -> str:
    
    for i in range(tries):

        #pause exectution of function to simulate human behaviour
        time.sleep(random.uniform(0.7, 1.6) + i * 0.8)  
        
        r = requests.get(url, headers=HEADERS, timeout=30)
        #request successful return HTML content
        if r.status_code == 200:
            return r.text
        # request bad, next itteration 
        if r.status_code in (429, 503):
            continue

        #not status code 200, 429 or 503, raise HTTP error 
        r.raise_for_status()
    raise SystemExit("Blocked")

# Parse HTML content and return as JSON-like dict
# if no products found or CAPTCHA detected, return empty dict
def parse_and_Dict(html_content:str) -> dict:
    #check for CAPTCHA in HTML content
    lower_html = html_content.lower()
    if "captchachallenge" in lower_html or "enter the characters you see below" in lower_html:
        print("Got CAPTCHA page")
        return [] #{STORE_NAME: []}   ##########################
    # results = {STORE_NAME: []}
    results = []
    soup = BeautifulSoup(html_content, "lxml")
    # uncomment below to debug html content
    # with open("finalAmzSoup.html", "w", encoding="utf-8") as f:
    #     f.write(str(soup))
    
    # select all divs with class 's-main-slot' && inside that dive any element with non empty data-asin attribute
    # data-asin is the unique identifier for each product on amazon
    product_cards = soup.select("div.s-main-slot [data-asin]:not([data-asin=''])")

    #no products found, return empty dict
    if not product_cards:
        print("No product cards found")
        return [] #{STORE_NAME: []} ###########################
    
    for c in product_cards:
        #product name 
        name = (c.select_one("h2 a span")
             or c.select_one("h2 span.a-text-normal")
             or c.select_one("h2"))
        prod_name = name.get_text(strip=True) if name else None
        
        # prodcuct price 
        price = c.select_one("span.a-price > span.a-offscreen")
        prod_price = price.get_text(strip=True) if price else "N/A"
        if prod_price != "N/A":
            prod_price = float(prod_price.replace("$", "").replace(",", ""))

        #product image
        img_tag = c.select_one("img.s-image")
        img_src = img_tag["src"] if img_tag and img_tag.get("src") else None

        #product Link 
        product_asin = c.get("data-asin")
        
        if product_asin:
            prod_link = f"https://www.amazon.ca/dp/{product_asin}"
        else:
            prod_link = None
     

        if prod_name:
            results.append({
                "store": STORE_NAME,
                "name": prod_name,
                "price": prod_price,
                "product_photo": img_src,
                "description": "No description available",
                "link": prod_link})
    
    return results

def search_products(search_term: str) -> list:
    
    search_url = build_url(search_term)
    html_content = get_HTML(search_url)
    item_list = parse_and_Dict(html_content)
    products = item_list

    return json.dumps(products) 


# main function for use as a script
if __name__ == "__main__":
    SEARCH_TERM = input("Enter search term: ").strip()
    # print("this is search term: " + SEARCH_TERM)
    search_url = build_url(SEARCH_TERM)
    html_content = get_HTML(search_url)
    item_list = parse_and_Dict(html_content)

    products = item_list

    if not products:
        print("No products were found")
    else:
        # print("this price type", type(prod_price))
        for index, product in enumerate(products, 1):
            print(f"Item {index}:")
            print(f"Name:  {product['name']}")
            print(f"Price: {product['price']}")
            print(f"Link:  {product['link']}")
            print(f"Image: {product['product_photo']}")
            print("-" * 60) # visual separator


