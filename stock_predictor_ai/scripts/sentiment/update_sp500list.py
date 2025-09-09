import pandas as pd
import os

# Base directory of your project (AI_Quant folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# This goes 3 levels up from sentiment/update_sp500list.py to AI_Quant

# Paths
RAW_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'sp500_list.xlsx')
CLEAN_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')

# Ensure raw folder exists
os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)

# Load original sp500 list if exists, else create empty
if os.path.exists(RAW_FILE):
    sp500 = pd.read_excel(RAW_FILE)
else:
    print("[!] sp500_list.xlsx not found, creating empty DataFrame")
    sp500 = pd.DataFrame(columns=[
        'Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry',
        'Headquarters Location', 'Date added', 'CIK', 'Founded'
    ])

# Normalize tickers in sp500 list
sp500['Symbol'] = sp500['Symbol'].astype(str).str.upper().str.replace('.', '-', regex=False).str.strip()

# Get tickers from clean folder
cleaned_files = [
    os.path.splitext(f)[0].upper().replace('.', '-').strip()
    for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx')
]

# Add missing tickers from clean folder
added_count = 0
for ticker in cleaned_files:
    if ticker not in sp500['Symbol'].values:
        sp500 = pd.concat([sp500, pd.DataFrame({
            'Symbol': [ticker],
            'Security': [None],
            'GICS Sector': [None],
            'GICS Sub-Industry': [None],
            'Headquarters Location': [None],
            'Date added': [None],
            'CIK': [None],
            'Founded': [None]
        })], ignore_index=True)
        added_count += 1

# Save updated sp500 list
sp500.to_excel(RAW_FILE, index=False)
print(f"[+] sp500_list.xlsx updated. Total tickers now: {len(sp500)} (added {added_count} new)")
