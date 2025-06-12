import feedparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import re
import os
import json

# Pinterest RSS feed URL
RSS_URL = "https://in.pinterest.com/Save_Sphere/feed.rss"

# Google Sheets setup
SHEET_ID = "1cBdL21Uq6Apcfalla0NSoyyK7PhfeTLGAyr7hDSU1Wk"  # Replace with your Google Sheet ID
SHEET_NAME = "Pinterest Pins" # Worksheet name
CREDENTIALS_FILE = "credentials.json"

# Load credentials from environment variable (for GitHub Actions)
if os.getenv("GOOGLE_CREDENTIALS"):
    credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

# Authenticate with Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Function to extract image URL from description
def extract_image_url(description):
    img_match = re.search(r'<img[^>]+src=["\'](.*?)["\']', description, re.IGNORECASE)
    return img_match.group(1) if img_match else ""

# Fetch RSS feed with retry
def fetch_rss_with_retry(url, retries=3):
    for attempt in range(retries):
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                raise Exception(f"Feed parsing failed: {feed.bozo_exception}")
            return feed
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep(5 * (2 ** attempt))
    raise Exception("Max retries exceeded for RSS feed")

# Fetch RSS feed
feed = fetch_rss_with_retry(RSS_URL)

# Extract pin details
pins = []
for entry in feed.entries:
    description = entry.get("description", "")
    pin = {
        "Title": entry.get("title", ""),
        "Link": entry.get("link", ""),
        "Image": extract_image_url(description),
        "Description": re.sub(r'<[^>]+>', '', description).strip(),  # Remove HTML tags
        "Published Date": entry.get("published", "")
    }
    pins.append(pin)

# Convert to DataFrame
df = pd.DataFrame(pins)

# Define headers
headers = ["Title", "Link", "Image", "Description", "Published Date"]

# Get existing data from sheet to avoid duplicates
try:
    existing_data = sheet.get_all_values()[1:]  # Skip header row
    existing_links = [row[1] for row in existing_data] if existing_data else []
except Exception as e:
    print(f"Error reading sheet: {e}")
    existing_links = []

# Filter out duplicates
new_pins = df[~df["Link"].isin(existing_links)]

# Write headers if sheet is empty
if not sheet.get_all_values():
    sheet.update("A1", [headers])

# Append new data
if not new_pins.empty:
    try:
        sheet.append_rows(new_pins[headers].values.tolist())
        print(f"Added {len(new_pins)} new pins to the sheet.")
    except Exception as e:
        print(f"Error appending rows: {e}")
        raise
else:
    print("No new pins to add.")

print("Google Sheet updated successfully!")