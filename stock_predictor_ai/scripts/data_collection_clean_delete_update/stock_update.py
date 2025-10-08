# stock_update.py
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def update_stocks(logger=None):
    """Update all cleaned stocks with today's data."""
    try:
        files = [f for f in os.listdir(CLEANED_FOLDER) if f.endswith(".csv")]
        if logger:
            logger(f"Updating {len(files)} cleaned stocks...")
        for idx, file in enumerate(files, start=1):
            ticker = file.replace(".csv", "")
            path = os.path.join(CLEANED_FOLDER, file)
            df = pd.read_csv(path, parse_dates=['Date'])
            stock = yf.Ticker(ticker)
            df_live = stock.history(period="1d", interval="1d")
            if df_live.empty:
                if logger:
                    logger(f"[!] No data for {ticker}. Skipping.")
                continue
            today = df_live.index[-1].date()
            if not df[df["Date"].dt.date == today].empty:
                if logger:
                    logger(f"[⏩] {ticker}: Already has today's data.")
                continue
            row = pd.DataFrame([{
                "Date": pd.to_datetime(today),
                f"Close_{ticker}": df_live["Close"].iloc[-1],
                f"High_{ticker}": df_live["High"].iloc[-1],
                f"Low_{ticker}": df_live["Low"].iloc[-1],
                f"Open_{ticker}": df_live["Open"].iloc[-1],
                f"Volume_{ticker}": int(df_live["Volume"].iloc[-1])
            }])
            df = pd.concat([df, row], ignore_index=True)
            df.to_csv(path, index=False)
            if logger:
                logger(f"[+] Updated {ticker} ({idx}/{len(files)})")
        return {"status": "success", "message": "All stocks updated successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
