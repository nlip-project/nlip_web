# module for UWO Deluce Bookstore

# imports for library functions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time

## CONSTANT VARIABLES
WEB_ADDRESS = 'https://bookstore.uwo.ca/'
SEARCH_ARG = 'search/products?search='
PAGE_NUM = "&page=" # no page number argument for fist page, second page starts at &page=1
SORT_ARG = "&sort=" # add search filter like: &sort=search_api_relevance%20DESC
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# takes a serch term or formatted query to search the site
# returns list of product objects
def search_product(query_term) -> list:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"user-agent={HTTP_HEADERS['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    product_list = []

    try:
        driver.get(WEB_ADDRESS + SEARCH_ARG + query_term)
        html = driver.page_source

        parsed_content = parse_site_content(html)
        # if first page is non-empty, query the next page. Otherwise no products matching the search term exist.
        if len(parsed_content) < 1:
            driver.quit()
            return

        product_list.append(parsed_content)

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
            product_list.append(parsed_content)
    finally:
        driver.quit()    

    return product_list

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

    return product_list

# parses out poduct information from html return
# returns list of dicts/json formatted objects
def parse_site_content(html_content) -> list:
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # message displayed if exceeded page with results, or if no results found
    end_of_results = soup.find_all("div", class_="view-empty")
    if len(end_of_results) != 0:
        return []

    product_information = []

    products = soup.find_all("div", class_="views-row")

    for prod in products:
        temp_prod = {}
        # extract item name
        temp_prod["item_name"] = prod.find('a').text


        # commerce-product-field is where price information is stored
        price_field = prod.find(class_="commerce-product-field")
        temp_prod["price"] = price_field.find("div", class_="field-item").text

        # add link to product page using link to item id stored in anchor tag
        temp_prod["link"] = (WEB_ADDRESS[:-1] + prod.find('a')['href'])

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
        "sort_arg_options": [], ## TODO: populate the valid search filters
        "http_headers": HTTP_HEADERS,
    }

# main function for use if run as script
if __name__ == "__main__":
    print("Input serch term: ")
    search_term = input()
    
    return_vals = search_product(search_term)
    print(return_vals)
    