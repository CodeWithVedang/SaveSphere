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

# User-Agent & Headers
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Categories
CATEGORIES = {
    "books": "https://www.amazon.in/gp/bestsellers/books/",
    "electronics": "https://www.amazon.in/gp/bestsellers/electronics/",
    "fashion": "https://www.amazon.in/gp/bestsellers/fashion/",
    "beauty": "https://www.amazon.in/gp/bestsellers/beauty/",
    "home_kitchen": "https://www.amazon.in/gp/bestsellers/home/",
    "appliances": "https://www.amazon.in/gp/bestsellers/appliances/",
    "baby": "https://www.amazon.in/gp/bestsellers/baby/",
    "grocery": "https://www.amazon.in/gp/bestsellers/grocery/",
    "toys_games": "https://www.amazon.in/gp/bestsellers/toys/",
    "automotive": "https://www.amazon.in/gp/bestsellers/automotive/"
    # Add more if needed
}

def fetch_products(category, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        print(f"[{category}] Status code: {res.status_code}")

        if "captcha" in res.text.lower():
            print(f"[{category}] ⚠️ CAPTCHA detected or blocked.")
            return []

        soup = BeautifulSoup(res.text, "lxml")
        product_list = soup.select("div.p13n-grid-content > div")
        print(f"[{category}] Products found: {len(product_list)}")

        if not product_list:
            print(f"[{category}] ⚠️ Selector not found. Amazon layout may have changed.")
            return []

        data = []
        for item in product_list[:10]:
            title_tag = item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
            link_tag = item.select_one("a.a-link-normal")
            price_tag = item.select_one(".a-price span.a-offscreen")

            title = title_tag.text.strip() if title_tag else ""
            link = "https://www.amazon.in" + link_tag["href"] if link_tag else ""
            price = price_tag.text.strip() if price_tag else ""

            data.append([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                category,
                title,
                link,
                price
            ])
        return data

    except Exception as e:
        print(f"[{category}] ❌ Error: {e}")
        return []


# Setup sheet headers
try:
    current = sheet.get_all_values()
    headers = current[0] if current else []
except Exception as e:
    print(f"❌ Sheet fetch error: {e}")
    headers = []

if not headers or headers != ["Date", "Category", "Title", "URL", "Price"]:
    sheet.clear()
    sheet.append_row(["Date", "Category", "Title", "URL", "Price"])

# Run scraper
all_data = []
for cat, url in CATEGORIES.items():
    all_data.extend(fetch_products(cat, url))

if all_data:
    try:
        sheet.append_rows(all_data, value_input_option="USER_ENTERED")
        print(f"✅ Added {len(all_data)} products.")
    except Exception as e:
        print(f"❌ Sheet write failed: {e}")
else:
    print("⚠️ No data scraped. Check logs above.")
