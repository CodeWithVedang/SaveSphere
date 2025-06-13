import os
import json
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Config
SHEET_ID = "1cBdL21Uq6Apcfalla0NSoyyK7PhfeTLGAyr7hDSU1Wk"  # Use your existing Sheet ID
SHEET_NAME = "Amazon Scrapped Data"
CREDENTIALS_FILE = "credentials.json"

# Load credentials from GitHub Actions environment
if os.getenv("GOOGLE_CREDENTIALS"):
    credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

# Authenticate with Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# Connect to sheet
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Amazon categories
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
    "automotive": "https://www.amazon.in/gp/bestsellers/automotive/",
    "sports_fitness": "https://www.amazon.in/gp/bestsellers/sports/",
    "pet_supplies": "https://www.amazon.in/gp/bestsellers/pet-supplies/",
    "jewellery": "https://www.amazon.in/gp/bestsellers/jewelry/",
    "musical_instruments": "https://www.amazon.in/gp/bestsellers/musical-instruments/",
    "video_games": "https://www.amazon.in/gp/bestsellers/videogames/",
    "watches": "https://www.amazon.in/gp/bestsellers/watches/",
    "luggage": "https://www.amazon.in/gp/bestsellers/luggage/",
    "handbags_wallets": "https://www.amazon.in/gp/bestsellers/luggage/1983338031/",
    "software": "https://www.amazon.in/gp/bestsellers/software/",
    "office_products": "https://www.amazon.in/gp/bestsellers/office-products/",
    "industrial_scientific": "https://www.amazon.in/gp/bestsellers/industrial/",
    "health_personal_care": "https://www.amazon.in/gp/bestsellers/hpc/",
}

HEADERS = {"User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0")}

def fetch_products(category, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "lxml")
        items = soup.select("ol#zg-ordered-list > li")
        data = []
        for li in items[:10]:
            title = li.select_one(".p13n-sc-truncate") or li.select_one(".a-size-medium")
            link = li.select_one("a.a-link-normal")
            price = li.select_one(".p13n-sc-price") or li.select_one(".a-offscreen")
            data.append([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                category,
                title.text.strip() if title else "",
                "https://amazon.in" + link["href"] if link else "",
                price.text.strip() if price else ""
            ])
        return data
    except Exception as e:
        print(f"Error fetching category {category}: {e}")
        return []

# Load current sheet data
try:
    existing_data = sheet.get_all_values()
    headers = existing_data[0]
except Exception as e:
    print(f"Sheet fetch error: {e}")
    headers = ["Date", "Category", "Title", "URL", "Price"]
    sheet.append_row(headers)

# Scrape and update
all_rows = []
for cat, url in CATEGORIES.items():
    all_rows.extend(fetch_products(cat, url))

if all_rows:
    try:
        sheet.append_rows(all_rows, value_input_option="USER_ENTERED")
        print(f"✅ Successfully added {len(all_rows)} products.")
    except Exception as e:
        print(f"❌ Failed to write to sheet: {e}")
else:
    print("⚠️ No data scraped.")
