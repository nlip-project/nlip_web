from amzpy import AmazonScraper

# Create scraper with default settings (amazon.com)
scraper = AmazonScraper()

# Fetch product details
url = "https://www.amazon.ca/Olaplex-Rich-Hydration-Mask-Cuticle/dp/B0FLTGFKPR/ref=sr_1_1_sspa?crid=1PD7K25Q3QU8M&dib=eyJ2IjoiMSJ9.U5W0cstTUnY_zz16rAT60y1bgCYKWUpqq21qktVfYBNqGdV3nuBQhwf5r1caQ0Cxo1jJfnrBsGY7cJKuih_B0-9SnyuqsIFEu2MPs5mtzFWKnCqgMZF5PvgXoTCmBIKPfZ0W4Ibux1uECVT4Y2WihDPiXF-p6eLGyahxBImdhE5IP6eX5z_ytpCd7TOHDiCFzsTB_tEoaBsP2EbJ8no4boD3PaDKok7pHaJsYVl4oZ0fdQrxLp8ZotZzKYRb-RUxSfOjeP5N1M4AGQ0maEf_iiSigHfLdLOfPIFUPUE4OWg.zqq558d5NSdLpwiflomgqCHWTIxwqjlMaXXQPxA6GkI&dib_tag=se&keywords=olaplex+no+7&qid=1760041656&sprefix=%2Caps%2C135&sr=8-1-spons&ufe=app_do%3Aamzn1.fos.a9cfdadb-853e-427d-a2b7-ed306eff4f60&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"
product = scraper.get_product_details(url)

if product:
    print(f"Title: {product['title']}")
    print(f"Price: {product['currency']}{product['price']}")
    print(f"Brand: {product['brand']}")
    print(f"Rating: {product['rating']}")
    print(f"Image URL: {product['img_url']}")




