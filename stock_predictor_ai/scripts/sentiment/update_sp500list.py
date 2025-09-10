import yfinance as yf
import pandas as pd
import os

# Base directory of your project (AI_Quant folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
SP500_FILE = os.path.join(CLEAN_FOLDER, 'sp500_list.xlsx')

# Ensure cleaned folder exists
os.makedirs(CLEAN_FOLDER, exist_ok=True)

# Get all tickers from the cleaned folder (ignore sp500_list.xlsx itself)
cleaned_files = [
    os.path.splitext(f)[0].upper().replace('.', '-').strip()
    for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx') and f != 'sp500_list.xlsx'
]

if not cleaned_files:
    print("[!] No stock files found in cleaned folder!")
    exit()

# List to store each ticker's information
tickers_info = []

for ticker in cleaned_files:
    print(f"Fetching info for {ticker}...")
    try:
        t = yf.Ticker(ticker)
        info = t.info

        tickers_info.append({
            'Symbol': ticker,
            'Security': info.get('shortName'),
            'GICS Sector': info.get('sector'),
            'GICS Sub-Industry': info.get('industry'),
            'Headquarters Location': info.get('city') + ", " + info.get('country') if info.get('city') and info.get('country') else None,
            'Date added': None,  # Can manually fill if needed
            'CIK': info.get('cik'),
            'Founded': info.get('founded')
        })
    except Exception as e:
        print(f"[!] Failed to fetch info for {ticker}: {e}")
        tickers_info.append({
            'Symbol': ticker,
            'Security': None,
            'GICS Sector': None,
            'GICS Sub-Industry': None,
            'Headquarters Location': None,
            'Date added': None,
            'CIK': None,
            'Founded': None
        })

# Create DataFrame and save
sp500_df = pd.DataFrame(tickers_info)
sp500_df.to_excel(SP500_FILE, index=False)
print(f"[+] sp500_list.xlsx updated. Total tickers: {len(sp500_df)}")
