import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Folder path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')

# Get all CSV files (like 'ABT.csv')
files = [f for f in os.listdir(CLEANED_FOLDER) if f.endswith(".csv")]

for file in files:
    ticker = file.replace(".csv", "")
    file_path = os.path.join(CLEANED_FOLDER, file)

    try:
        # Read the existing CSV file
        df = pd.read_csv(file_path, parse_dates=['Date'])

        # Fetch today's data
        stock = yf.Ticker(ticker)
        df_live = stock.history(period="1d", interval="1d")

        if df_live.empty:
            print(f"⚠ No data for {ticker}. Skipping. Possibly delisted, please check.")
            continue

        # Extract today's row
        today = df_live.iloc[-1]
        today_date = df_live.index[-1].date()

        # Format it like existing data
        new_row = pd.DataFrame([{
            "Date": pd.to_datetime(today_date),
            f"Close_{ticker}": today["Close"],
            f"High_{ticker}": today["High"],
            f"Low_{ticker}": today["Low"],
            f"Open_{ticker}": today["Open"],
            f"Volume_{ticker}": int(today["Volume"])
        }])

        # Check if today's data already exists
        if not df[df["Date"].dt.date == today_date].empty:
            print(f"⏩ {ticker}: Already has today's data.")
            continue

        # Append and save as CSV
        df_updated = pd.concat([df, new_row], ignore_index=True)
        df_updated.to_csv(file_path, index=False)
        print(f"✅ Updated {ticker}")

    except Exception as e:
        print(f"❌ Failed to update {ticker}: {e}")
