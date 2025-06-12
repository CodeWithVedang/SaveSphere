import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re
import os
import json

# Google Sheets setup
SHEET_ID = "1cBdL21Uq6Apcfalla0NSoyyK7PhfeTLGAyr7hDSU1Wk"  # Replace with your Google Sheet ID
SHEET_NAME = "Pinterest Pins"  # Worksheet name
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

# Function to extract Amazon affiliate link from description
def extract_affiliate_link(description):
    amzn_link = re.search(r'https://amzn\.to/[^\s]+', description)
    return amzn_link.group(0) if amzn_link else ""

# Read existing sheet data
try:
    sheet_data = sheet.get_all_values()
    if not sheet_data:
        print("Sheet is empty. No data to process.")
        exit(0)
except Exception as e:
    print(f"Error reading sheet: {e}")
    exit(1)

# Convert to DataFrame
headers = sheet_data[0]
data = sheet_data[1:] if len(sheet_data) > 1 else []
df = pd.DataFrame(data, columns=headers)

# Add Affiliate Link column if it doesn't exist
if "Affiliate Link" not in df.columns:
    df["Affiliate Link"] = ""

# Extract affiliate links from Description
df["Affiliate Link"] = df["Description"].apply(extract_affiliate_link)

# Update headers in the sheet
updated_headers = headers + ["Affiliate Link"] if "Affiliate Link" not in headers else headers
sheet.update("A1", [updated_headers])

# Update sheet with data
try:
    sheet.update("A2", df.values.tolist())
    print(f"Updated sheet with Affiliate Link column. Processed {len(df)} rows.")
except Exception as e:
    print(f"Error updating sheet: {e}")
    exit(1)

print("Affiliate links extraction completed successfully!")