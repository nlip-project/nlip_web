# Website Modules

This folder contains the *website_modules* which act as an interface between the client and the website.

A module for each site is needed to facilitate quering and parsing the resulting information for various brands and stores.

## Requirements

When used with nlip_web the following packages have to be added to poetry:

1. `poetry add beautifulsoup4`
2. `poetry add selenium`
3. `poetry add requests`

** Server side requiremments**

- [NLIP Server](https://github.com/nlip-project/nlip_server), is required to use the libraries provided
- [NLIP SDK](https://github.com/nlip-project/nlip_sdk), is required for development

## Module Structure

The [main module](./main_module.py) can be used to query a search term through every site which is currently supported, and return a list of json objects representing the results from each site.

Each module has a primary function: **search_product(search_term: str)**. The function will return a json object representing the search results for the *search term*.

## Examples

A [Hello World Program](./hello_world/) can be found in its respective folder.

Module files are commonly used in a similar fashion to a library, although some can be run as [scripts](./dellelce_bookstore_module.py) to test the usage.

## Output

```json
{
  <store_name>: [
    {
      "name": "string",
      "price": "string",
      "sizes": [
        "string"
      ],
      "availability": "string",
      "product_photo": "string",
      "link": "string"
    }
  ]
}

```