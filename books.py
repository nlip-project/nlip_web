import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/page-1.html"

htmlPage = requests.get(URL)                   # fetch page
soup = BeautifulSoup(htmlPage.content, "html.parser")  # parse page

with open("BookSoup_output.txt", "w", encoding="utf-8") as f:
    f.write(soup.prettify())


articles = soup.select("article.product_pod")
print("hello\n\n\n\n\n")


# write each article's raw HTML to file
with open("booklist.txt", "w", encoding="utf-8") as f:
    # f.clear()
    # f.write(articles.prettify())
    for i, article in enumerate(articles, start=1):
        f.write(f"--- BOOK {i} START ---\n")
        f.write(article.prettify())
        f.write(f"\n--- BOOK {i} END ---\n\n")





with open("bookList2.txt", "w", encoding="utf-8") as f:
    for book in articles:
        f.write("*****************\n")
        f.write(book.prettify())
        f.write("\n\n\n\n\n\n\n\n")
        title = book.h3.a["title"]
        price = book.select_one(".price_color").get_text(strip=True)
        print("\n\n\n",title, "\n-", price)

