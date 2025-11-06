import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode



SEARCH_TERM = input("Enter search term: ").strip()
def build_url(q: str) -> str:
    return "https://www.amazon.ca/s?" + urlencode({"k": q})

URL = build_url(SEARCH_TERM)

soup = BeautifulSoup(requests.get(URL).content, "html.parser")

with open("soup_output.txt", "w", encoding="utf-8") as f:
    f.write(soup.prettify())