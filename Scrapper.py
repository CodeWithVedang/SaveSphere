import os, requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
gs = gspread.authorize(creds)
wb = gs.open_by_key(os.getenv("SHEET_ID"))

def fetch_trending(url):
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "lxml")
    items = soup.select("ol#zg-ordered-list > li")
    result = []
    for li in items[:10]:
        title = li.select_one(".p13n-sc-truncate") or li.select_one(".a-size-medium")
        link = li.select_one("a.a-link-normal")
        price = li.select_one(".p13n-sc-price") or li.select_one(".a-offscreen")
        result.append({
            "title": title.text.strip() if title else "",
            "url": "https://amazon.in" + link["href"] if link else "",
            "price": price.text.strip() if price else "",
        })
    return result

def update_sheet():
    sheet_name = "Amazon Scrapped Data"
    try:
        sheet = wb.worksheet(sheet_name)
    except:
        sheet = wb.add_worksheet(title=sheet_name, rows=1000, cols=6)
        sheet.append_row(["Date", "Category", "Title", "URL", "Price"])

    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    all_rows = []

    for cat, url in CATEGORIES.items():
        products = fetch_trending(url)
        for p in products:
            all_rows.append([date, cat, p["title"], p["url"], p["price"]])

    sheet.append_rows(all_rows, value_input_option="USER_ENTERED")

if __name__ == "__main__":
    update_sheet()
