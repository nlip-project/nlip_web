import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

URL = "https://www.costco.ca/s"
PARAMS = {"langId": "-24", "keyword": "laptop"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
    "Referer": "https://www.costco.ca/",
    "Connection": "close",
}

# retry on transient network issues (NOT on 403/429)
retry = Retry(
    total=2, connect=2, read=2,
    backoff_factor=0.6,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

with requests.Session() as s:
    s.headers.update(HEADERS)
    s.mount("https://", HTTPAdapter(max_retries=retry))

    print("step 1", flush=True)
    try:
        # separate timeouts: (connect_timeout, read_timeout)
        resp = s.get(URL, params=PARAMS, timeout=(10, 25), allow_redirects=True)
        print("step 2", flush=True)
        print(f"status={resp.status_code} final_url={resp.url}", flush=True)
    except requests.exceptions.Timeout:
        print("ERROR: request timed out", flush=True)
        raise
    except requests.exceptions.RequestException as e:
        print(f"ERROR: request failed: {e}", flush=True)
        raise

    # Save whatever HTML we actually got (even if 403/block page)
    html = resp.text
    with open("CostcoSoup_output.txt", "w", encoding="utf-8") as f:
        f.write(html)

    # Quick peek at the first 500 chars to see if it's a bot page
    print("sample:", html[:500].replace("\n"," ")[:500], flush=True)

    # Optional parse (may just parse a block page)
    soup = BeautifulSoup(resp.content, "html.parser")
    print("done", flush=True)
