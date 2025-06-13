import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuration
SHEET_ID = "1cBdL21Uq6Apcfalla0NSoyyK7PhfeTLGAyr7hDSU1Wk"
SHEET_NAME = "Amazon Scrapped Data"
CREDENTIALS_FILE = "credentials.json"

# Load credentials from GitHub Secrets
if os.getenv("GOOGLE_CREDENTIALS"):
    credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

# Authenticate
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Headers
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Categories
CATEGORIES = {
    "books": "https://www.amazon.in/gp/bestsellers/books/",
    "electronics": "https://www.amazon.in/gp/bestsellers/electronics/",
    "beauty": "https://www.amazon.in/gp/bestsellers/beauty/",
    "baby": "https://www.amazon.in/gp/bestsellers/baby/",
    "toys_games": "https://www.amazon.in/gp/bestsellers/toys/",
    "automotive": "https://www.amazon.in/gp/bestsellers/automotive/"
}

def fetch_products(category, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        print(f"[{category}] Status code: {res.status_code}")

        if "captcha" in res.text.lower():
            print(f"[{category}] ⚠️ CAPTCHA detected.")
            return []

        soup = BeautifulSoup(res.text, "lxml")
        product_list = soup.select("div.p13n-grid-content > div")
        print(f"[{category}] Products found: {len(product_list)}")

        results = []
        for i, item in enumerate(product_list[:10], 1):
            title_tag = item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
            link_tag = item.select_one("a.a-link-normal")
            price_tag = item.select_one(".a-price span.a-offscreen")

            title = title_tag.text.strip() if title_tag else ""
            link = "https://www.amazon.in" + link_tag["href"] if link_tag else ""
            price = price_tag.text.strip() if price_tag else ""

            results.append([i, title, link, price])
        return results

    except Exception as e:
        print(f"[{category}] ❌ Error: {e}")
        return []

def clear_sheet():
    try:
        sheet.clear()
        print("✅ Sheet cleared before writing new data.")
    except Exception as e:
        print(f"⚠️ Error clearing sheet: {e}")

def write_category_section(start_row, category, data):
    section_header = [[f"Category: {category}"]]
    table_header = [["Sr No", "Product Name", "URL", "Price"]]
    sheet.update(f"A{start_row}", section_header)
    sheet.update(f"A{start_row + 1}", table_header)
    sheet.update(f"A{start_row + 2}", data)

def run_scraper():
    clear_sheet()
    current_row = 1

    for cat, url in CATEGORIES.items():
        products = fetch_products(cat, url)
        if products:
            write_category_section(current_row, cat, products)
            current_row += len(products) + 4  # Leave space between tables
        else:
            print(f"[{cat}] No data written.")
    print("✅ Scraper finished writing all categories.")

if __name__ == "__main__":
    run_scraper()
