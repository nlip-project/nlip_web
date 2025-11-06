import requests
from bs4 import BeautifulSoup

URL = "https://www.google.com/search?q=laptop&rlz=1C5OZZY_enCA1169CA1169&oq=laptop&gs_lcrp=EgZjaHJvbWUyCQgAEEUYORiABDIKCAEQABixAxiABDIKCAIQABixAxiABDIKCAMQABixAxiABDINCAQQABiDARixAxiABDIKCAUQABixAxiABDIGCAYQRRg8MgYIBxBFGDzSAQgxMjkwajBqN6gCALACAA&sourceid=chrome&ie=UTF-8"

htmlPage = requests.get(URL)                   # fetch page
soup = BeautifulSoup(htmlPage.content, "html.parser")  # parse page

with open("GoogSoup_output.txt", "w", encoding="utf-8") as f:
    f.write(soup.prettify())