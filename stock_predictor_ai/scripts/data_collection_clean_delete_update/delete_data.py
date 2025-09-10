import os
import pandas as pd
import yfinance as yf
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

    # Remove delisted files from raw folder
    for ticker in delisted:
        raw_path = os.path.join(RAW_FOLDER, f"{ticker}.xlsx")
        if os.path.exists(raw_path):
            os.remove(raw_path)
            print(f"[+] Removed {raw_path}")

    # Remove delisted files from cleaned folder
    for ticker in delisted:
        clean_path = os.path.join(CLEAN_FOLDER, f"{ticker}.xlsx")
        if os.path.exists(clean_path):
            os.remove(clean_path)
            print(f"[+] Removed {clean_path}")

# -----------------------------
# Save updated sp500_list.xlsx
# -----------------------------
sp500.to_excel(RAW_FILE, index=False)
print(f"[+] sp500_list.xlsx updated. Total tickers now: {len(sp500)}")
