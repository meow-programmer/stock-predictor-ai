import yfinance as yf
import pandas as pd
import random
import os
import requests

# --------------------------
# Set base directories
# --------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_FOLDER, exist_ok=True)  # Ensure folder exists

# --------------------------
# Fetch S&P 500 tickers (fix for HTTP 403)
# --------------------------
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise error if request fails

sp500 = pd.read_html(response.text)[0]
all_tickers = sp500['Symbol'].tolist()
all_tickers = [ticker.replace('.', '-') for ticker in all_tickers]  # Yahoo format

# --------------------------
# Ask user what to do
# --------------------------
print("Choose an option:")
print("1. Download 100 random S&P 500 stocks")
print("2. Download a specific stock")
print("3. Download a custom number of random S&P 500 stocks")
print("4. Exit")

choice = input("Enter 1, 2, 3, or 4: ").strip()

# --------------------------
# Function to download stocks
# --------------------------
def download_stocks(tickers):
    for ticker in tickers:
        file_path = os.path.join(RAW_FOLDER, f'{ticker}.xlsx')
        if os.path.exists(file_path):
            print(f"[=] Skipped (already exists): {ticker}")
            continue
        try:
            df = yf.download(ticker, period='max')
            df.to_excel(file_path)
            print(f"[+] Saved: {ticker}")
        except Exception as e:
            print(f"[!] Failed: {ticker} - {e}")

# --------------------------
# Option handling
# --------------------------
existing_files = [os.path.splitext(f)[0] for f in os.listdir(RAW_FOLDER) if f.endswith('.xlsx')]

if choice == '1':
    remaining_tickers = [t for t in all_tickers if t not in existing_files]
    if len(remaining_tickers) == 0:
        print("[!] All S&P 500 stocks already downloaded!")
    else:
        num_to_download = min(100, len(remaining_tickers))
        random_stocks = random.sample(remaining_tickers, num_to_download)
        download_stocks(random_stocks)

elif choice == '2':
    ticker = input("Enter stock ticker (e.g., TSLA, NVDA, AMZN): ").upper().replace('.', '-')
    download_stocks([ticker])

elif choice == '3':
    try:
        num_to_download = int(input("How many random stocks do you want to download? ").strip())
        if num_to_download <= 0:
            raise ValueError
    except ValueError:
        print("[!] Invalid number. Exiting.")
        exit()

    remaining_tickers = [t for t in all_tickers if t not in existing_files]
    if len(remaining_tickers) == 0:
        print("[!] All S&P 500 stocks already downloaded!")
    else:
        if num_to_download > len(remaining_tickers):
            print(f"[!] Only {len(remaining_tickers)} remaining. Downloading all remaining.")
            num_to_download = len(remaining_tickers)
        random_stocks = random.sample(remaining_tickers, num_to_download)
        download_stocks(random_stocks)

elif choice == '4':
    print("Exiting...")

else:
    print("Invalid input. Please run again and enter 1, 2, 3, or 4.")
