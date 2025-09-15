import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Folder path
cleaned_folder = "stock_predictor_ai/data/cleaned"

# Get all Excel files (like 'ABT.xlsx')
files = [f for f in os.listdir(cleaned_folder) if f.endswith(".xlsx")]

for file in files:
    ticker = file.replace(".xlsx", "")
    file_path = os.path.join(cleaned_folder, file)

    try:
        # Read the existing Excel file
        df = pd.read_excel(file_path)

        # Fetch today's data
        stock = yf.Ticker(ticker)
        df_live = stock.history(period="1d", interval="1d")

        if df_live.empty:
            print(f"⚠ No data for {ticker}. Skipping. Possibly delisted please check.")
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

        # Append and save
        df_updated = pd.concat([df, new_row], ignore_index=True)
        df_updated.to_excel(file_path, index=False)
        print(f"✅ Updated {ticker}")

    except Exception as e:
        print(f"❌ Failed to update {ticker}: {e}")
