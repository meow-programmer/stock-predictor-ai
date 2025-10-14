# fetch_data.py
import os
import pandas as pd
import random
import yfinance as yf
import requests
from .clean_data import clean_data_auto  # auto-clean function

# === Paths ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..'))
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def fetch_stocks(choice="random_100", ticker=None, num=None, min_num=None, max_num=None, logger=None):
    """
    Download stocks from yfinance and auto-clean.
    - choice: "random_100", "single", "custom", "range"
    """
    try:
        # Reset ticker when not needed
        if choice != "single":
            ticker = None

        # Get S&P 500 tickers
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        sp500 = pd.read_html(requests.get(url, headers=headers).text)[0]
        all_tickers = [t.replace('.', '-') for t in sp500['Symbol'].tolist()]

        existing = [os.path.splitext(f)[0] for f in os.listdir(RAW_FOLDER) if f.endswith('.csv')]
        remaining = [t for t in all_tickers if t not in existing]

        if choice == "random_100":
            to_download = random.sample(remaining, min(100, len(remaining)))
        elif choice == "single" and ticker:
            to_download = [ticker]
        elif choice == "custom" and num:
            to_download = random.sample(remaining, min(num, len(remaining)))
        elif choice == "range" and min_num and max_num:
            count = random.randint(min_num, max_num)
            to_download = random.sample(remaining, min(count, len(remaining)))
        else:
            return {"status": "error", "message": "Invalid parameters."}
    
    except Exception as e:
        print("⚠️ Error while fetching stocks:", e)
    