# module for walmart.ca/en/

import requests
from bs4 import BeautifulSoup
import json
import cloudscraper
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time

## CONSTANT VARIABLES
WEB_ADDRESS = 'https://www.walmart.ca/en/'
SEARCH_ARG = 'search?q='
SORT_ARG = '&sort='
SORT_ARG_OPTIONS = ['price_low','price_high','best_match']
FILTER_CATEGORY = '&catId=' ## integer value representing category
## page numbering starts at 1 for first page
PAGE_NUM = '&page=' ## defaults to being paired with: AFFINITY_OVERRIDE
AFFINITY_OVERRIDE = '&affinityOverride=default'

FILTER_BRAND = '&facet=brand%3A' ## brand%3a + string
## for multiple brands concat with: %7C%7C
## &facet=brand%3APentel%7C%7Cbrand%3ABIC

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

# return list of constant variables and configurable options
def get_config() -> dict:
    return {
        "web_address": WEB_ADDRESS,
        "search_arg": SEARCH_ARG,
        "page_num": PAGE_NUM,
        "affinity_override": AFFINITY_OVERRIDE,
        "sort_arg": SORT_ARG,
        "sort_arg_options": SORT_ARG_OPTIONS, ## TODO: populate the valid search filters
        "filter_category" :FILTER_CATEGORY,
        "filter_brand": FILTER_BRAND,
        "http_headers": HTTP_HEADERS,
    }

def search_product(search_term):

    options = Options()
    ##options.add_argument("--headless=new")
    options.add_argument(f"user-agent={HTTP_HEADERS['User-Agent']}")
    ##options.add_argument("--no-sandbox")
    ##options.add_argument("--disable-dev-shm-usage")
    ##options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    url = WEB_ADDRESS + SEARCH_ARG + search_term
    try:
        driver.get(url=url)

        time.sleep(5)

        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    
    return soup

def parse_site_content(html_content) -> list:
    return []

# main function for use as a script
if __name__ == "__main__":
    print("Input serch term: ")
    search_term = input()
    
    return_vals = search_product(search_term)
    print(return_vals)