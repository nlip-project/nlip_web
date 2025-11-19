# imports for library functions
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import sys
import json

from concurrent.futures import ThreadPoolExecutor, as_completed

# Import search modules for websites
from . import newegg_ca_module
from . import  dellelce_bookstore_module 
from . import  staples_ca_module
# from . import  walmart_ca_module

# THREAD COUNT
MAX_THREADS = 4
THREAD_PREFIX = "main_module_thread_"

# Modules with completed search_product(str) functions
search_modules = [
    dellelce_bookstore_module,
    newegg_ca_module, 
    staples_ca_module
]

def single_thread_search_product(search_term: str):
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

    res = {}
    res['results'] = search_results

    # has to return a proper python dictionary
    return res

# func for thread to execute
def run_module_search(module: str, search_term: str, ):
    if not hasattr(module, 'search_product'):
        return None
    
    try:
        search_function = getattr(module, 'search_product')
        product_results_json = search_function(search_term)
            
        # convert to dict
        prods = json.loads(product_results_json)
        return(prods)

    except Exception as e:
        print(f'ERROR with {module}\n')
        print(f'\tFunction: [search_product(str) -> json]')
        print(f'\t{e}\n')
        return None

def search_product(search_term: str):
    search_results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix=THREAD_PREFIX) as executor:
        ## exectute
        future = {
            executor.submit(run_module_search, module, search_term): module
            for module in search_modules
        }

        for future in as_completed(future):
            result = future.result()
            if result is not None:
                search_results.append(result)

    # has to return a proper python dictionary
    res = {}
    res['results'] = search_results
    return res

def main():    
    search_term = ""
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        print("Input serch term: ")
        search_term = input()

    #test_performance()
    print(search_product(search_term))

# benchmark test for multi vs single thread performance
def test_performance():
    search_term = "lanyards"

    t1 = time.perf_counter()
    print(single_thread_search_product(search_term))
    t2 = time.perf_counter()

    t3 = time.perf_counter()
    print(search_product(search_term))
    t4 = time.perf_counter()

    print(f'Single thread took :{t2 - t1} seconds')
    print(f'Mutli thread took :{t4 - t3} seconds')

# for use of main module as script
if __name__ == "__main__":
    main()