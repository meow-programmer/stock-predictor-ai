import yfinance as yf
import pandas as pd
import random
import requests
import os

# Determine the proper data folder path (always points to the existing data/raw)
DATA_FOLDER = os.path.join(os.path.dirname(__file__), '../../data/raw')
os.makedirs(DATA_FOLDER, exist_ok=True)  # Only creates if it doesn't exist

# Ensure sp500_list.xlsx exists
sp500_file = os.path.join(DATA_FOLDER, 'sp500_list.xlsx')
if not os.path.exists(sp500_file):
    print("[*] sp500_list.xlsx not found. Downloading current S&P 500 list...")

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error if the request failed

    # Use pandas to read HTML from the content
    sp500 = pd.read_html(response.text)[0]
    sp500.to_excel(sp500_file, index=False)
    print("[+] sp500_list.xlsx created!")
else:
    sp500 = pd.read_excel(sp500_file)

# Clean tickers for Yahoo Finance
all_tickers = [ticker.replace('.', '-') for ticker in sp500['Symbol'].tolist()]

# Ask the user
print("Choose an option:")
print("1. Download 100 random S&P 500 stocks")
print("2. Download a specific stock")
print("3. Add more random S&P 500 stocks")
print("4. Exit")

choice = input("Enter 1, 2, 3, or 4: ").strip()


def download_stocks(tickers):
    for ticker in tickers:
        file_path = os.path.join(DATA_FOLDER, f'{ticker}.xlsx')
        if os.path.exists(file_path):
            print(f"[=] Skipped (already exists): {ticker}")
            continue
        try:
            df = yf.download(ticker, period='max')
            df.to_excel(file_path)
            print(f"[+] Saved: {ticker}")
        except Exception as e:
            print(f"[!] Failed: {ticker} - {e}")


if choice == '1':
    random_100 = random.sample(all_tickers, 100)
    download_stocks(random_100)

elif choice == '2':
    ticker = input("Enter stock ticker (e.g., TSLA, NVDA, AMZN): ").upper().replace('.', '-')
    download_stocks([ticker])

elif choice == '3':
    try:
        num_to_add = int(input("How many new random stocks do you want to add? ").strip())
    except ValueError:
        print("Invalid number. Exiting.")
        exit()

    existing_files = [f.split('.')[0] for f in os.listdir(DATA_FOLDER) if f.endswith('.xlsx')]
    remaining_tickers = [t for t in all_tickers if t not in existing_files]

    if len(remaining_tickers) == 0:
        print("All S&P 500 stocks already downloaded!")
    else:
        if num_to_add > len(remaining_tickers):
            print(f"Only {len(remaining_tickers)} new stocks available. Downloading all remaining.")
            num_to_add = len(remaining_tickers)
        new_stocks = random.sample(remaining_tickers, num_to_add)
        download_stocks(new_stocks)

elif choice == '4':
    print("Exiting...")

else:
    print("Invalid input. Please run again and enter 1, 2, 3, or 4.")
