import yfinance as yf
import pandas as pd
import random
import os

# Ask the user
print("Choose an option:")
print("1. Download 100 random S&P 500 stocks")
print("2. Download a specific stock")
print("3. Exit")


choice = input("Enter 1 or 2: ").strip()

# Create directory
os.makedirs('data/raw', exist_ok=True)

if choice == '1':
    # Step 1: Get all tickers from S&P 500 list
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    all_tickers = sp500['Symbol'].tolist()

    # Clean up tickers (e.g., BRK.B -> BRK-B for Yahoo)
    all_tickers = [ticker.replace('.', '-') for ticker in all_tickers]

    # Step 2: Pick random 100
    random_100 = random.sample(all_tickers, 100)

    # Step 3: Download all
    for ticker in random_100:
        file_path = f'data/raw/{ticker}.xlsx'
        if os.path.exists(file_path):
            print(f"[=] Skipped (already exists): {ticker}")
            continue
        try:
            df = yf.download(ticker, period='max')
            df.to_excel(f'data/raw/{ticker}.xlsx')
            print(f"[+] Saved: {ticker}")
        except Exception as e:
            print(f"[!] Failed: {ticker} - {e}")
    

elif choice == '2':
    ticker = input("Enter stock ticker (e.g., TSLA, NVDA, AMZN): ").upper().replace('.', '-')
    try:
        df = yf.download(ticker, period='max')
        df.to_excel(f'data/raw/{ticker}.xlsx')
        print(f"[+] Saved: {ticker}")
    except Exception as e:
        print(f"[!] Failed to download {ticker} - {e}")

else:
    print("Invalid input. Please run again and enter 1 or 2.")

