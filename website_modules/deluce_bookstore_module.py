# module for UWO Deluce Bookstore

# imports for library functions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json

## CONSTANT VARIABLES
STORE_NAME = "deulce_bookstore"
WEB_ADDRESS = 'https://bookstore.uwo.ca/'
SEARCH_ARG = 'search/products?search='
PAGE_NUM = "&page=" # no page number argument for fist page, second page starts at &page=1
SORT_ARG = "&sort=" # add search filter like: &sort=search_api_relevance%20DESC
## options = [relevance_desc, newest to oldest, oldest to newest, price increasing, price decreasing]
SORT_ARG_OPTIONS = ['search_api_relevance%20DESC', 'created+DESC', 'created+ASC', 'search_api_aggregation_2+ASC', 'search_api_aggregation_2+DESC']
CATEGORY = '&category='
CATEGORY_OPTIONS = ['All'] # All is default, category id can be specified 
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# takes a serch term or formatted query to search the site
# returns list of product objects
def search_product(query_term):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={HTTP_HEADERS['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    product_list = {}
    product_list[STORE_NAME] = []

    try:
        driver.get(WEB_ADDRESS + SEARCH_ARG + query_term)
        html = driver.page_source

        parsed_content = parse_site_content(html)
        # if first page is non-empty, query the next page. Otherwise no products matching the search term exist.
        if len(parsed_content) < 1:
            driver.quit()
            return

        product_list[STORE_NAME] = product_list[STORE_NAME] + parsed_content

        # first page non-empty, query remaining pages of content.
        end_of_content = False
        current_page = 1 # second page starts at 1
        while not end_of_content:
            # sleep to not overwhelm site with continuous queries
            time.sleep(5)
            driver.get(WEB_ADDRESS + SEARCH_ARG + query_term + PAGE_NUM + str(current_page))
            parsed_content = parse_site_content(driver.page_source)

            if len(parsed_content) < 1:
                # end of query content
                break
            # increment page counter
            current_page += 1
            product_list[STORE_NAME] = product_list[STORE_NAME] + parsed_content
    finally:
        driver.quit()    

    return json.dumps(product_list)

# return search results from a specific page
def search_product_specific_page(query_term, pagenum) -> list:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={HTTP_HEADERS['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    product_list = []

    try:
        driver.get(WEB_ADDRESS + SEARCH_ARG + query_term + PAGE_NUM + str(pagenum))
        html = driver.page_source

        parsed_content = parse_site_content(html)
        # if first page is non-empty, query the next page. Otherwise no products matching term exist.
        if len(parsed_content) < 1:
            driver.quit()
            return

        product_list.append(parsed_content)
    finally:
        driver.quit()    

    return json.dumps(product_list)

# parses out poduct information from html return
# returns list of dicts/json formatted objects
def parse_site_content(html_content) -> list:
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # message displayed if exceeded page with results, or if no results found
    end_of_results = soup.find_all("div", class_="view-empty")
    if len(end_of_results) != 0:
        return []

    products = soup.find_all("div", class_="views-row")
    
    # create the dictionary to return list of product information
    product_information = []

    for prod in products:
        temp_prod = {}
        # extract it-em name
        temp_prod["name"] = prod.find('a').text

        temp_prod["description"] = 'N/A'

        # commerce-product-field is where price information is stored
        price_field = prod.find(class_="commerce-product-field")
        temp_prod["price"] = price_field.find("div", class_="field-item").text
        ## can potentially contain <del>price<del> If item is on sale.

        # check if item has sizes:
        sizes_radio_group = prod.find(class_='attribute-widgets')
        temp_prod['sizes'] = ['N/A']
        
        if sizes_radio_group != None:
            temp_prod['sizes'] = []
            radio_buttons = prod.find_all(class_="control-label")
            for opt in radio_buttons:
                if opt.text == 'Size:': ## skip control values with non-size specific information
                    continue
                temp_prod['sizes'].append(opt.text)

        ## TODO: fix availability for items with multiple sizes
        availability = prod.find(class_="add-to-cart").text
        temp_prod["availability"] = availability

        if availability == "Add to cart":
            availability = "in stock"

        img_src = prod.find('img')['src']

        # if image is the placeholder for no photo, make it ""
        # nlip_web_client will filter this as NO IMAGE
        if img_src == "/sites/all/themes/bookstore/images/no-photo.png":
            img_src = ""

        temp_prod["product_photo"] = img_src

        # add link to product page using link to item id stored in anchor tag
        temp_prod["link"] = (WEB_ADDRESS[:-1] + prod.find('a')['href'])

        ## Further product information available on the item page
        # Stock count
        # on order count
        # SKU -> differs from product id. is different for each size listing

        # push product information to list
        product_information.append(temp_prod)

    return product_information

def get_web_address() -> str:
    return WEB_ADDRESS

# return list of constant variables and configurable options
def get_config() -> dict:
    return {
        "web_address": WEB_ADDRESS,
        "search_arg": SEARCH_ARG,
        "page_num": PAGE_NUM,
        "sort_arg": SORT_ARG,
        "sort_arg_options": SORT_ARG_OPTIONS,
        "http_headers": HTTP_HEADERS,
        "filter_category": CATEGORY,
        "filter_category_options": CATEGORY_OPTIONS
    }

# main function for use if run as script
if __name__ == "__main__":
    search_term = ""
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        print("Input serch term: ")
        search_term = input()
    
    print(search_product(search_term))
    