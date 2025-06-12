import feedparser
import gspread
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup

# --- CONFIG ---
RSS_URL = 'https://in.pinterest.com/Save_Sphere/feed.rss'
SHEET_NAME = 'Pinterest Pins'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# Load service account from environment variable file
CREDENTIALS_FILE = 'credentials.json'  # will come from GitHub secret
# ---------------

def extract_image(html_description):
    soup = BeautifulSoup(html_description, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else ''

def main():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sheet = gc.open(SHEET_NAME).sheet1

    # Parse RSS feed
    feed = feedparser.parse(RSS_URL)
    sheet.clear()
    sheet.append_row(['Title', 'Link', 'Image', 'Description', 'Published Date'])

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        description = entry.description
        pub_date = entry.published
        img_url = extract_image(description)
        sheet.append_row([title, link, img_url, description, pub_date])

if __name__ == "__main__":
    main()
