import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.costco.ca/s?langId=-24&keyword=laptop"


def _build_options(user_data_dir: Path | None, headless: bool = False) -> Options:
    opts = Options()
    if user_data_dir:
        opts.add_argument(f"--user-data-dir={str(user_data_dir)}")
        # can optionally set a specific profile directory inside the user-data-dir:
        # opts.add_argument("--profile-directory=Default")

    if headless:
        # keep non-headless for Costco unless you really need headless
        opts.add_argument("--headless=new")

    # Lessen automation fingerprints
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_experimental_option("detach", True)  # keep window open after script ends (handy for debugging)

    # Normal-ish UA (not strictly necessary if using real profile)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    return opts

def make_driver():
    """
    Attempt 1: Use your real Chrome profile (best for Costco cookies/region).
    If it's locked, Attempt 2: use a dedicated project profile folder.
    """
    # macOS default Chrome profile root:
    real_profile_root = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    opts = _build_options(real_profile_root)

    try:
        driver = webdriver.Chrome(options=opts)
        driver.set_window_size(1400, 1000)
        return driver
    except SessionNotCreatedException as e:
        # Likely “user data directory in use”
        print("[warn] Real Chrome profile is locked (Chrome running). "
              "Retrying with a dedicated Selenium profile...")
        # Dedicated project-local profile dir:
        project_profile = Path.cwd() / ".selenium-profile"
        project_profile.mkdir(exist_ok=True)
        # Optionally start clean each run:
        # shutil.rmtree(project_profile, ignore_errors=True); project_profile.mkdir(parents=True, exist_ok=True)

        opts2 = _build_options(project_profile)
        driver = webdriver.Chrome(options=opts2)
        driver.set_window_size(1400, 1000)
        return driver


def looks_like_chrome_interstitial(driver) -> bool:
    # Chrome’s offline/blocked interstitial has these bits
    try:
        title = driver.title or ""
        body_html = driver.page_source or ""
        return ("icon-offline" in body_html) or (title.strip() == "www.costco.ca")
    except Exception:
        return False

def handle_cookie_or_region(driver):
    """
    Try to accept cookie / region banners if present. If you see one manually,
    just click it and the script will continue.
    """
    candidates = [
        # common cookie/region buttons Costco uses (varies)
        (By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"),           # OneTrust consent
        (By.CSS_SELECTOR, "button#truste-consent-button"),                  # TrustArc
        (By.CSS_SELECTOR, "button[data-automation='accept-button']"),
        (By.CSS_SELECTOR, "button:has(span:contains('Accept'))"),           # Chromium supports :has(), but not always
        (By.XPATH, "//button[contains(., 'Accept') or contains(., 'agree') or contains(., 'Agree')]"),
        (By.XPATH, "//button[contains(., 'Continue') or contains(., 'Got it')]"),
    ]
    for how, sel in candidates:
        try:
            btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((how, sel)))
            btn.click()
            time.sleep(0.5)
            break
        except Exception:
            pass

def wait_for_products(driver, timeout=25):
    """
    Wait for any of several product-tile selectors Costco uses.
    Returns (locator_tuple, list_of_webelements)
    """
    tile_locators = [
        (By.CSS_SELECTOR, "[data-automation='product-tile']"),
        (By.CSS_SELECTOR, "div.product-tile"),
        (By.CSS_SELECTOR, "div.product-grid-item"),
        (By.CSS_SELECTOR, "div.product"),
        (By.XPATH, "//a[@data-automation='product-tile-description']/ancestor::*[self::div or self::li][1]"),
    ]

    end = time.time() + timeout
    last_err = None
    while time.time() < end:
        for loc in tile_locators:
            try:
                tiles = driver.find_elements(*loc)
                if tiles:
                    return loc, tiles
            except Exception as e:
                last_err = e
        time.sleep(0.5)
    raise TimeoutError(f"Product tiles not found. Last error: {last_err}")

def extract_from_tile(tile):
    """
    Attempt multiple selectors for title/price/link inside a tile.
    """
    def first_text(selectors):
        for how, sel in selectors:
            try:
                el = tile.find_element(how, sel)
                txt = el.text.strip()
                if txt:
                    return txt
            except Exception:
                pass
        return ""

    def first_attr(selectors, attr):
        for how, sel in selectors:
            try:
                el = tile.find_element(how, sel)
                val = el.get_attribute(attr) or ""
                if val:
                    return val
            except Exception:
                pass
        return ""

    title = first_text([
        (By.CSS_SELECTOR, "[data-automation='product-tile-description']"),
        (By.CSS_SELECTOR, "a.product-tile-description"),
        (By.CSS_SELECTOR, "a[data-automation='product-title']"),
        (By.CSS_SELECTOR, ".product-name, .description, h2, h3, a"),
    ])

    price = first_text([
        (By.CSS_SELECTOR, "[data-automation='product-price']"),
        (By.CSS_SELECTOR, ".price, .currency, .amount, [class*='price'] span"),
        (By.XPATH, ".//*[contains(text(),'$') or contains(text(),'CA$')]"),
    ])

    link = first_attr([
        (By.CSS_SELECTOR, "a[href][data-automation='product-tile-description']"),
        (By.CSS_SELECTOR, "a.product-tile-description[href]"),
        (By.CSS_SELECTOR, "a[href]"),
    ], "href")

    return {
        "title": title,
        "price": price,
        "link": link,
    }

def scroll_to_load(driver, steps=6, pause=0.6):
    html = driver.find_element(By.TAG_NAME, "html")
    for _ in range(steps):
        html.send_keys(Keys.END)
        time.sleep(pause)

def main():
    driver = make_driver()
    try:
        print("step 1: open url")
        driver.get(URL)
        time.sleep(2)

        # If you see a cookie/region wall, we try to accept; if not found, it's fine.
        handle_cookie_or_region(driver)

        # Quick interstitial check
        if looks_like_chrome_interstitial(driver):
            print("[ERROR] Chrome interstitial/offline page detected (network/VPN/CDN block).")
            print("        Try: disable VPN, switch networks, or run headed with your profile and refresh.")
            Path("costco_interstitial.html").write_text(driver.page_source, encoding="utf-8")
            return

        # Give the page some breathing room
        time.sleep(2)

        # Scroll to trigger lazy-load
        scroll_to_load(driver, steps=6, pause=0.7)

        print("step 2: wait for product tiles")
        loc, tiles = wait_for_products(driver, timeout=30)
        print(f"[debug] found {len(tiles)} tiles via {loc}")

        # Gather results (limit to a reasonable number)
        items = []
        for t in tiles[:60]:
            data = extract_from_tile(t)
            if data["title"] or data["price"] or data["link"]:
                items.append(data)

        if not items:
            print("[warn] no items parsed — saving HTML for inspection.")
            Path("costco_search_page.html").write_text(driver.page_source, encoding="utf-8")
            return

        # Save CSV
        out = Path("costco_laptops.csv")
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["title", "price", "link"])
            w.writeheader()
            for row in items:
                w.writerow(row)

        print(f"done. saved {len(items)} products to {out.resolve()}")
        # also print a few
        for p in items[:10]:
            print(f"- {p['title']} | {p['price']} | {p['link']}")

    finally:
        # Keep the browser open for a moment so you can see the page if needed
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    main()
