#!/usr/bin/env python3
"""
walmart_search.py
Search Walmart Canada (walmart.ca) for a query and print products from the first page.

Requires:
  pip install requests beautifulsoup4

Usage:
  python hello.py "paper towels"
  python hello.py "paper towels" --out json
  python hello.py "paper towels" --out csv --file results.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}
BASE = "https://www.walmart.ca"


@dataclass
class Product:
    name: str
    price: Optional[str]
    min_order_qty: Optional[str]
    max_order_qty: Optional[str]
    availability: Optional[str]
    rating: Optional[str]
    review_count: Optional[str]
    link: str
    in_stock: bool


def _safe_get(d: Dict[str, Any], path: Iterable[str], default: Any = None) -> Any:
    """Safely get a nested value from dict using a list/iterable path."""
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _extract_price(item: Dict[str, Any]) -> Optional[str]:
    """Try multiple known fields for price; return a string if found."""
    pi = item.get("priceInfo", {}) or {}
    candidates = [
        pi.get("linePrice"),
        pi.get("currentPrice"),
        pi.get("priceString"),
        _safe_get(pi, ["price", "priceString"]),
        _safe_get(pi, ["price", "price"]),
    ]
    for c in candidates:
        if c is None:
            continue
        # Normalize to string
        return str(c)
    return None


def _extract_items_from_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Walmart's Next.js payload stores results at:
    props.pageProps.initialData.searchResult.itemStacks[*].items[*]
    Ads or other blocks may be mixed in.
    """
    items: List[Dict[str, Any]] = []
    stacks = _safe_get(data, ["props", "pageProps", "initialData", "searchResult", "itemStacks"], [])
    if not isinstance(stacks, list):
        return items
    for stack in stacks:
        stack_items = stack.get("items") or []
        if isinstance(stack_items, list):
            items.extend(stack_items)
    return items


def parse_products(html: str) -> List[Product]:
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="_NEXT_DATA_")
    if not script or not script.string:
        return []

    try:
        payload = json.loads(script.string)
    except json.JSONDecodeError:
        return []

    raw_items = _extract_items_from_json(payload)
    products: List[Product] = []

    for item in raw_items:
        name = item.get("name")
        if not name:  # skip non-product blocks
            continue

        price = _extract_price(item)
        order_min = item.get("orderMinLimit")
        order_max = item.get("orderLimit")
        availability = item.get("availabilityStatusDisplayValue")
        rating_info = item.get("rating") or {}
        rating = rating_info.get("averageRating")
        review_count = rating_info.get("numberOfReviews")

        canonical = item.get("canonicalUrl")
        link = f"{BASE}{canonical}" if canonical else BASE

        # Consider it a valid product if it has a name and a link
        if not canonical:
            continue

        avail_str = str(availability).strip() if availability is not None else ""
        in_stock = "in stock" in avail_str.lower()

        products.append(
            Product(
                name=str(name),
                price=str(price) if price is not None else None,
                min_order_qty=str(order_min) if order_min is not None else None,
                max_order_qty=str(order_max) if order_max is not None else None,
                availability=avail_str or None,
                rating=str(rating) if rating is not None else None,
                review_count=str(review_count) if review_count is not None else None,
                link=link,
                in_stock=in_stock,
            )
        )

    return products


def search_walmart(query: str, timeout: int = 20) -> List[Product]:
    url = f"{BASE}/search?query={quote(query)}"
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return parse_products(resp.text)


def print_pretty(products: List[Product]) -> None:
    in_stock = [p for p in products if p.in_stock]
    oos = [p for p in products if not p.in_stock]

    print(f"Number of products in stock: {len(in_stock)}")
    print("PRODUCTS IN STOCK:\n")
    for p in in_stock:
        _print_product(p)
        print()

    print("-" * 110 + "\n")
    print(f"Number of products out of stock: {len(oos)}")
    print("PRODUCTS OUT OF STOCK:\n")
    for p in oos:
        _print_product(p)
        print()


def _print_product(p: Product) -> None:
    fields = [
        ("Name", p.name),
        ("Price", p.price),
        ("Min Order Quantity", p.min_order_qty),
        ("Max Order Quantity", p.max_order_qty),
        ("Availability", p.availability),
        ("Rating", p.rating),
        ("Review Count", p.review_count),
        ("Link", p.link),
    ]
    for label, value in fields:
        if value is not None:
            print(f"{label}: {value}")


def write_json(products: List[Product], file: Optional[str]) -> None:
    data = [asdict(p) for p in products]
    if file:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON to {file}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def write_csv(products: List[Product], file: Optional[str]) -> None:
    rows = [asdict(p) for p in products]
    fieldnames = list(rows[0].keys()) if rows else [
        "name", "price", "min_order_qty", "max_order_qty",
        "availability", "rating", "review_count", "link", "in_stock"
    ]
    if file:
        with open(file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved CSV to {file}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Search Walmart.ca and print first-page products.")
    ap.add_argument("query", help="Product search query (e.g., 'toilet paper')")
    ap.add_argument("--out", choices=["pretty", "json", "csv"], default="pretty",
                    help="Output format (default: pretty)")
    ap.add_argument("--file", help="Optional output file path for json/csv")
    ap.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds (default: 20)")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    try:
        products = search_walmart(args.query, timeout=args.timeout)
    except requests.HTTPError as e:
        print(f"HTTP error from Walmart: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.out == "pretty":
        print_pretty(products)
    elif args.out == "json":
        write_json(products, args.file)
    elif args.out == "csv":
        write_csv(products, args.file)
    else:
        print_pretty(products)


if __name__ == "__main__":
    main()
