# imports for library functions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
import importlib

# Import search modules for websites
import newegg_ca_module
import dellelce_bookstore_module 
import staples_ca_module 
import walmart_ca_module

# Modules with completed search_product(str) functions
search_modules = [
    dellelce_bookstore_module,
    newegg_ca_module, 
    staples_ca_module
    ]

def search_product(search_term: str) -> list:
    search_results = []    
    for module in search_modules:

        if not hasattr(module, 'search_product'):
            continue
        
        search_function = getattr(module, 'search_product')

        try:
            product_results_json = search_function(search_term)
            
            # convert to dict
            prods = json.loads(product_results_json)
            search_results.append(prods)

        except Exception as e:
            print(f'ERROR with {module}\n')
            print(f'\tFunction: [search_product(str) -> json]')
            print(f'\t{e}\n')

    return json.dumps(search_results)

# for use of main module as script
if __name__ == "__main__":
    search_term = ""
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        print("Input serch term: ")
        search_term = input()
    
    print(search_product(search_term))