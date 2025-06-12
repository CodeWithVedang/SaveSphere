import feedparser
import gspread
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup

# --- CONFIG ---
RSS_URL = 'https://in.pinterest.com/Save_Sphere/feed.rss'
SHEET_NAME = 'Pinterest Pins'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# --- Service Account Key (Embedded) ---
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "gen-lang-client-0407272446",
  "private_key_id": "bc40bbc3e4e551d9d77c49dede921bba05a8c7ea",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCm5fRXTdCBHE62
0OdOHkJcBt21TwaATBJLhUB6t9b0TEmmNZ9ng4c4EiP8r2j4tO/5TC39O22Vh3XB
Tw3pCfB8hLYzDfRGfBEtXNGKgzQSMEeZYEn2t27qOWDkg4erGTfT7/g8q/YWb3m+
Oyf81cWHMf+RUVp15vFEuCR5Pf2190M+sA5/ydCDs/F0ibfsLYAjh7uneSwzmZYB
cK1W8buW2rR/A0kuOr1xoR9Bv0HgcDwjAEYdPue0u5g6lxW85c/Mo7twPjRJs0Vl
iX9hxBMS7hq4fxYCXvIY5DEdAVu1YFonMZ715nfv8ok6UXiO1/Hmucdn9Gi4G2kM
VCnV2ui3AgMBAAECggEAQdYva2sWR4Afqu1AeWflXIEW32lTkrOvedwQQfiYUllv
qiG4BnDzm9JIIOsfGRDjIzACakURpu0/Lejd/2I83BnL99rW1CEn84GMZTv5g/1I
mT/LHYhhuAK3bp1WHM//XlrozSI2msYRu9GBJjM7zueRvcTeTukxnp6XQL6MAUXr
fgtvx3o5X+Qetdx/0Jj3lRQodQmQrWlZtkDTqRFKwzh7N2DqrWNCyy9eqHH3dmGy
K1Vo5dmwBAynMjrfnIAoLZUXgXoPqLMN+tImN8psMXeCi9q9alI5yrfM++SvQVzP
3/uwJAo1v6UAnr3PRugGZisfjfn1KRnQO814ZkSIYQKBgQDkSUxVnAgu7VeFFr9M
EqqOZwnRKnccC/0sxJt8Xyc6Bo2xwpGwchwgxVYSMwZAARqkR9bIGlWRQk3P6cTM
qxw7mzFgPzKRVrSB3y9o9GujiHsDJtg+aEselrBVlOgkk/L96mh09iYfMnB0gHGF
hDfMqrRvIjYdqR+fLEwWxWzv1wKBgQC7KNU1qjL0drkfettfUTpWr2YKhToNv6p7
J6V3xUjgWoYX4ki/u26WHP6zXTFFo/fjDdnwh3zsYDY6XKx/7LhoDlwt19rAmB1K
dxD+QE2ls+TOK1VDnapnpeUEpOmg09yPpb1u+zo7SEMVrJ3EWE0pMEL6yx9mJ9p/
ot4mpMgyIQKBgQDBPZq0TSRQNPCE5ECCcLqXWHli6YNx5mQlZTgJC7L0119SPdV9
etp8kw7M0QxVWZnnvjf9ou0TzQB5IvVIGwAHJNOjGVwA01hxJy/GtD/5aipW/KbI
DRiph/00NJxdei+S6L4LY+HZPqUauS9fShDB2y5pdJhCe0sdPi4aiHwyeQKBgDuG
pSlIVKSEDiUBAjyyrQddCetWrDwrNaGt3mbVjHQu1m9KPTEd//ImjqulfEJWAEVq
5mIl9YmIoDa3uvWE6LHPv2mlOaH/v3ErpW/4K7oEGUWpapjy0Hveu5RajyPjvkbB
xBpENSUduphuKk+EdiYff24cpIPtMQVfW6CW0EWBAoGAfPKlmA1sgh533mCZ3L/b
oY6tVrmLwR6a0TmRH9vxS3mcXvzXGQqnL9wJgvqdInLsh9lnolzCw4kLB0grpOOM
FhTFlANRf3nsUpJTUzlODGdNqC4CsSyQh02lEu6vC4zMBuMOUqIExqLqduBKcGAP
6p4PRrIy7/bhFWOT7IEEDuE=
-----END PRIVATE KEY-----""",
  "client_email": "pinterest-rss-updater@gen-lang-client-0407272446.iam.gserviceaccount.com",
  "client_id": "104332942046693524951",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pinterest-rss-updater%40gen-lang-client-0407272446.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# ---------------------------------------

def extract_image(html_description):
    soup = BeautifulSoup(html_description, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else ''

def main():
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sheet = gc.open(SHEET_NAME).sheet1

    sheet.clear()
    sheet.append_row(['Title', 'Link', 'Image', 'Description', 'Published Date'])

    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        description = entry.description
        pub_date = entry.published
        img_url = extract_image(description)
        sheet.append_row([title, link, img_url, description, pub_date])

if __name__ == "__main__":
    main()
