# https://stackoverflow.com/questions/68992032/scrape-walmart-search-results-python helped me figure out how to make search request for Walmart
# Prints all the products found on walmart.ca with a specified product name on the first page
# Must install bs4 -> BeautifulSoup and requests to work
from bs4 import BeautifulSoup  # For parsing HTML
import requests  # For getting into Newegg and using its search function
import json  # For formatting the data so it is easy to read/extract info
from urllib.parse import quote  # Proper formatting of link

STORE_NAME = 'new_egg_ca'
WEB_ADDRESS = 'https://www.newegg.ca/'
SEARCH_ARG = 'p/pl?d='

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    #'Accept-Language': 'en-US,en;q=0.9',
    #'Accept-Encoding': 'gzip, deflate, br',
    #'Connection': 'keep-alive',
}

def get_url(product_name, page):
    return 'https://www.newegg.ca/p/pl?d=' + quote(product_name)


def print_products(items):
    products = []
    # Get only product blocks, format them
    for item in items:
        # Product Name
        title_tag = item.select_one(".item-title")
        title = title_tag.text.strip() if title_tag else None
        link = title_tag.get("href") if title_tag else None

        # Price
        dollars_tag = item.select_one(".price-current strong")
        cents_tag = item.select_one(".price-current sup")
        price = None
        if dollars_tag:
            dollars = dollars_tag.text.strip()
            cents = cents_tag.text.strip() if cents_tag else "00"
            price = f"{dollars}{cents}"

        # Image
        img_tag = item.select_one("img")
        image = img_tag.get("src") if img_tag else None

        # Shipping
        shipping_tag = item.select_one(".price-ship")
        shipping = shipping_tag.text.strip() if shipping_tag else None

        if title and price:  # Only add if title found (skip ads)
            products.append({
                "name": title,
                "price": price,
                "link": link,
                "product_photo": image,
                "shipping_info": shipping
            })

    # How many products that were on the first page
    num_of_products = len(products)
    if num_of_products > 0:
        print("Number of products in stock: " + str(len(products)))
        # Print out all products found on the first page
        print("PRODUCTS IN STOCK:\n")
        for p in products:
            for attribute in p:
                print(attribute + ": " + str(p[attribute]))
            print()

    return products

def search_product(product_name: str):
    product_list = {}
    product_list[STORE_NAME] = []

    try:
        session = requests.Session()
        session.headers.update(HTTP_HEADERS)

        url = get_url(product_name, 1)

        r = session.get(url)  # Pretend to be browser, prevent Walmart from flagging us as a bot
        soup = BeautifulSoup(r.text, 'html.parser')  # No need to install lxml (html.parser), parse HTML

        # Same method of extracting info as Staples
        product_list[STORE_NAME]  = print_products(soup.select('.item-cell'))
        # If you want more pages, just ask and add next page to url and redo this process with that page (ex. &page2)
    except Exception as e:
        print(e)

    return json.dumps(product_list)


# Search loop
if __name__ == "__main__":
    searching = 'y'
    while searching == 'y':
        product_desc = input("Enter the name of the product: ")
        search_product(product_desc)

        user_input = input("Perform another search? (y/n): ")
        searching = user_input[0].lower()
        while searching != 'y' and searching != 'n':
            searching = input("Perform another search? (y/n): ")

    print("Thank you for shopping at Walmart!")
