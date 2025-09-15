import os
import pandas as pd
import yfinance as yf
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# Base directories and paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'sp500_list.xlsx')
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
CLEAN_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')

# Ensure directories exist
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)

# -----------------------------
# Load sp500_list.xlsx
# -----------------------------
if os.path.exists(RAW_FILE):
    sp500 = pd.read_excel(RAW_FILE)
else:
    print("[!] sp500_list.xlsx not found. Creating empty DataFrame")
    sp500 = pd.DataFrame(columns=['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry',
                                  'Headquarters Location', 'Date added', 'CIK', 'Founded'])

# -----------------------------
# Check delisted tickers in parallel
# -----------------------------
def is_delisted(ticker):
    try:
        info = yf.Ticker(ticker).info
        if 'regularMarketPrice' not in info or info['regularMarketPrice'] is None:
            return ticker
    except Exception:
        return ticker
    return None

tickers = sp500['Symbol'].tolist()
delisted = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(is_delisted, t): t for t in tickers}
    for future in as_completed(futures):
        result = future.result()
        if result:
            delisted.append(result)

if not delisted:
    print("[+] No delisted tickers found.")
else:
    print(f"[!] Found {len(delisted)} delisted tickers: {delisted}")

    # Remove delisted from sp500 DataFrame
    sp500 = sp500[~sp500['Symbol'].isin(delisted)]

    # Remove delisted files from raw + cleaned
    for ticker in delisted:
        for folder in [RAW_FOLDER, CLEAN_FOLDER]:
            file_path = os.path.join(folder, f"{ticker}.xlsx")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[+] Removed {file_path}")

# -----------------------------
# Extra option: delete N random tickers
# -----------------------------
delete_random = input("Do you want to delete random tickers? (y/n): ").strip().lower()

if delete_random == "y":
    try:
        n = int(input("How many random tickers do you want to delete?: ").strip())
        if n > 0 and n <= len(sp500):
            random_tickers = random.sample(sp500['Symbol'].tolist(), n)
            print(f"[!] Randomly deleting {n} tickers: {random_tickers}")

            # Remove from dataframe
            sp500 = sp500[~sp500['Symbol'].isin(random_tickers)]

            # Remove files
            for ticker in random_tickers:
                for folder in [RAW_FOLDER, CLEAN_FOLDER]:
                    file_path = os.path.join(folder, f"{ticker}.xlsx")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[+] Removed {file_path}")

        else:
            print(f"[!] Invalid number. Must be between 1 and {len(sp500)}")
    except ValueError:
        print("[!] Invalid input. Skipping random delete.")

# -----------------------------
# Save updated sp500_list.xlsx
# -----------------------------
sp500.to_excel(RAW_FILE, index=False)
print(f"[+] sp500_list.xlsx updated. Total tickers now: {len(sp500)}")
