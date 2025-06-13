
# 🛒 SaveSphere Amazon Scraper & Pinterest Integration Bot

Welcome to **SaveSphere**, an innovative bot that automates the process of scraping top Amazon products, integrating Pinterest RSS feeds, and managing affiliate links—all seamlessly synced to Google Sheets! 🚀 This repository powers a dynamic system to track trending Amazon deals and showcase them via Pinterest, making it a perfect tool for affiliate marketers, deal hunters, and automation enthusiasts.

---

## ✨ Features That Make SaveSphere Shine

- **Amazon Product Scraper** 🛍️
  - Scrapes top 10 best-selling products from Amazon categories like Books, Electronics, Beauty, Baby, Toys & Games, and Automotive.
  - Extracts product titles, URLs, and prices with precision using BeautifulSoup and lxml.
  - Automatically updates a Google Sheet with neatly organized category-wise tables.

- **Pinterest RSS Integration** 📌
  - Fetches the latest pins from the Save Sphere Pinterest account via RSS feed.
  - Extracts pin titles, links, images, descriptions, and publication dates.
  - Filters duplicates to ensure only new pins are added to the Google Sheet.

- **Affiliate Link Extraction** 🔗
  - Automatically extracts Amazon affiliate links (e.g., `amzn.to`) from Pinterest pin descriptions.
  - Updates the Google Sheet with affiliate links for easy tracking and management.

- **Dynamic Web Display** 🌐
  - A sleek, responsive web interface built with HTML, CSS, and JavaScript.
  - Displays Pinterest pins with images and titles, styled with Pinterest’s signature red theme.
  - Supports light/dark mode with automatic theme switching based on time of day.

- **Automation with GitHub Actions** ⏰
  - Scheduled workflows to run the Amazon scraper daily at 11:00 AM IST.
  - Hourly updates for Pinterest RSS feed and affiliate link extraction.
  - Securely handles Google Sheets authentication using GitHub Secrets.

- **Error Handling & Reliability** 🛡️
  - Robust retry logic for RSS feed fetching to handle network issues.
  - CAPTCHA detection for Amazon scraping to avoid bot blocks.
  - Comprehensive logging for debugging and monitoring.

---

## 🛠️ How It Works

### 1. Amazon Scraper (`amazon_scrapper.py`)
- **What it does**: Scrapes the top 10 products from specified Amazon bestseller categories.
- **Process**:
  - Sends HTTP requests with a custom User-Agent to mimic a browser.
  - Parses HTML using BeautifulSoup to extract product details (title, URL, price).
  - Clears the Google Sheet and writes category-wise tables with headers.
- **Output**: A Google Sheet (`Amazon Scrapped Data`) with organized product data.

### 2. Pinterest RSS to Google Sheets (`pinterest_to_sheets.py`)
- **What it does**: Fetches and processes pins from the Save Sphere Pinterest RSS feed.
- **Process**:
  - Parses the RSS feed using `feedparser` to extract pin details.
  - Extracts image URLs from descriptions and removes HTML tags.
  - Filters out duplicate pins by checking existing links in the Google Sheet.
  - Appends new pins to the `Pinterest Pins` worksheet.
- **Output**: A Google Sheet with columns for Title, Link, Image, Description, Published Date, and Affiliate Link.

### 3. Affiliate Link Extraction (`extract_affiliate_links.py`)
- **What it does**: Extracts Amazon affiliate links from pin descriptions.
- **Process**:
  - Reads the `Pinterest Pins` worksheet into a Pandas DataFrame.
  - Uses regex to find `amzn.to` links in descriptions.
  - Adds or updates the `Affiliate Link` column in the Google Sheet.
- **Output**: Updated Google Sheet with affiliate links for each pin.

### 4. Web Interface (`index.html`, `style.css`, `script.js`)
- **What it does**: Displays Pinterest pins in a visually appealing grid.
- **Process**:
  - Fetches the Pinterest RSS feed via a CORS proxy (`api.allorigins.win`).
  - Dynamically renders pins with images, titles, and links to Pinterest.
  - Features a responsive design with light/dark mode and smooth animations.
- **Output**: A user-friendly webpage showcasing Save Sphere’s latest pins.

### 5. GitHub Actions Workflows
- **Amazon Scraper Workflow** (`amazon_scrapper.yml`):
  - Runs daily at 11:00 AM IST.
  - Sets up Python, installs dependencies, and executes `amazon_scrapper.py`.
- **Pinterest Update Workflow** (`pinterest_update.yml`):
  - Runs hourly.
  - Executes `pinterest_to_sheets.py` and `extract_affiliate_links.py` sequentially.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Google Cloud Project with Sheets and Drive API enabled
- Google Service Account credentials (`credentials.json`)
- GitHub repository with Secrets configured:
  - `GOOGLE_CREDENTIALS`: JSON string of Google Service Account credentials
  - `USER_AGENT`: Custom User-Agent string for Amazon scraping

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/savesphere-bot.git
   cd savesphere-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Google Sheets**:
   - Create a Google Sheet with two worksheets: `Amazon Scrapped Data` and `Pinterest Pins`.
   - Update `SHEET_ID` in `amazon_scrapper.py`, `pinterest_to_sheets.py`, and `extract_affiliate_links.py` with your Sheet ID.

4. **Configure GitHub Secrets**:
   - Add `GOOGLE_CREDENTIALS` and `USER_AGENT` to your repository’s Secrets in GitHub Settings.

5. **Run Locally** (optional):
   ```bash
   python amazon_scrapper.py
   python pinterest_to_sheets.py
   python extract_affiliate_links.py
   ```

6. **Deploy Web Interface**:
   - Host `index.html`, `style.css`, and `script.js` on a static hosting service (e.g., GitHub Pages, Netlify).
   - Ensure the Pinterest RSS feed URL is accessible via a CORS proxy.

### GitHub Actions Setup
- The workflows (`amazon_scrapper.yml` and `pinterest_update.yml`) are pre-configured to run automatically.
- Manually trigger workflows via the GitHub Actions tab if needed.

---

## 📊 Bot Specialities

- **Efficiency**: Automates repetitive tasks like scraping and data syncing, saving hours of manual work.
- **Scalability**: Easily extendable to scrape more Amazon categories or integrate other RSS feeds.
- **User-Friendly Interface**: A modern, responsive web display with Pinterest-inspired aesthetics.
- **Reliability**: Built-in error handling and retry mechanisms ensure consistent performance.
- **Customizable**: Modular scripts allow easy tweaks for different use cases (e.g., new categories, different platforms).

---

## 📈 Example Output

### Google Sheet: Amazon Scrapped Data
| Category: Books |       |       |       |
|----------------|-------|-------|-------|
| Sr No | Product Name | URL | Price |
| 1 | Book Title | https://amazon.in/... | ₹499 |
| ... | ... | ... | ... |

### Google Sheet: Pinterest Pins
| Title | Link | Image | Description | Published Date | Affiliate Link |
|-------|------|-------|-------------|---------------|----------------|
| Cool Gadget | https://pinterest.com/... | https://pinimg.com/... | Check out this deal! | 2025-06-13 | https://amzn.to/... |

### Web Interface
A grid of Pinterest pins with images, titles, and clickable links, styled with smooth animations and a toggleable dark/light theme.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests.
- Submit pull requests with improvements or new features.
- Add support for more Amazon categories or other affiliate platforms.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgements

- Built by [CodeWithVedang](https://github.com/CodeWithVedang)
- Powered by Python, BeautifulSoup, feedparser, gspread, and GitHub Actions
- Inspired by the need to automate affiliate marketing workflows

---

**Happy Deal Hunting with SaveSphere!** 🛒📌

