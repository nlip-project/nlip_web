#!/bin/bash

# Ask the user for input
read -p "Enter search term: " search_term

# Run the Python module with the provided input
python3 -m website_modules.main_module "$search_term"
