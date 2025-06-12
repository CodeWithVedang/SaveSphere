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
# Add at the top of the script
# Load credentials from environment variable
credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
with open("credentials.json", "w") as f:
    json.dump(credentials, f)
    
# Google Sheets setup
SHEET_ID = "1cBdL21Uq6Apcfalla0NSoyyK7PhfeTLGAyr7hDSU1Wk"  # Replace with your Google Sheet ID
SHEET_NAME = "Pinterest Pins"  # Worksheet name
CREDENTIALS_FILE = "credentials.json"


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

# Fetch RSS feed
feed = feedparser.parse(RSS_URL)
if feed.bozo:
    raise Exception("Failed to parse RSS feed")

# Extract pin details
pins = []
for entry in feed.entries:
    description = entry.get("description", "")
    pin = {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "image": extract_image_url(description),
        "description": re.sub(r'<[^>]+>', '', description).strip(),  # Remove HTML tags
        "published_date": entry.get("published", "")
    }
    pins.append(pin)

# Convert to DataFrame
df = pd.DataFrame(pins)

# Get existing data from sheet to avoid duplicates
try:
    existing_data = sheet.get_all_values()[1:]  # Skip header row
    existing_links = [row[1] for row in existing_data] if existing_data else []
except Exception as e:
    print(f"Error reading sheet: {e}")
    existing_links = []

# Filter out duplicates
new_pins = df[~df["link"].isin(existing_links)]

# Define headers
headers = ["Title", "Link", "Image", "Description", "Published Date"]

# Write headers if sheet is empty
if not sheet.get_all_values():
    sheet.update("A1", [headers])

# Append new data
if not new_pins.empty:
    sheet.append_rows(new_pins[headers].values.tolist())
    print(f"Added {len(new_pins)} new pins to the sheet.")
else:
    print("No new pins to add.")

print("Google Sheet updated successfully!")