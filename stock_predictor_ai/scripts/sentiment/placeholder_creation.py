import os
import pandas as pd
from datetime import datetime

# -----------------------------
# Directories
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
SENTIMENT_FOLDER = os.path.join(BASE_DIR, 'data', 'company_sentiment_ready')
os.makedirs(SENTIMENT_FOLDER, exist_ok=True)

# Today's date
today = pd.to_datetime(datetime.today().date())

# -----------------------------
# Get all stock files
# -----------------------------
stock_files = [
    f for f in os.listdir(CLEANED_FOLDER)
    if f.endswith(('.xlsx', '.csv')) and f != 'sp500_list.xlsx'
]

if not stock_files:
    print("[!] No stock files found in cleaned folder!")
    exit()

# -----------------------------
# Update or create sentiment Excel files
# -----------------------------
for file_name in stock_files:
    company = os.path.splitext(file_name)[0]
    stock_file = os.path.join(CLEANED_FOLDER, file_name)
    sentiment_file = os.path.join(SENTIMENT_FOLDER, f'{company}_sentiment.xlsx')

    # Read stock file
    try:
        if file_name.endswith('.xlsx'):
            df_stock = pd.read_excel(stock_file, parse_dates=['Date'], engine='openpyxl')
        else:
            df_stock = pd.read_csv(stock_file, parse_dates=['Date'])
    except Exception as e:
        print(f"[!] Skipping {company}: cannot read file ({e})")
        continue

    # Only trading dates from stock file
    trading_dates = df_stock['Date'].sort_values().unique()

    # Read existing sentiment Excel if exists
    if os.path.exists(sentiment_file):
        df_sentiment = pd.read_excel(sentiment_file, parse_dates=['Date'], engine='openpyxl')
        last_date = df_sentiment['Date'].max()
    else:
        df_sentiment = pd.DataFrame(columns=['Date', 'Sentiment'])
        last_date = pd.Timestamp.min  # very early date

    # Determine new dates to add (only trading dates after last_date)
    new_dates = [d for d in trading_dates if d > last_date]
    if new_dates:
        new_rows = pd.DataFrame({'Date': new_dates, 'Sentiment': 0.0})
        df_sentiment = pd.concat([df_sentiment, new_rows], ignore_index=True)
        df_sentiment = df_sentiment.sort_values('Date').reset_index(drop=True)
        df_sentiment.to_excel(sentiment_file, index=False, engine='openpyxl')
        print(f"[+] {company}_sentiment.xlsx updated with {len(new_rows)} new trading dates.")
    else:
        print(f"[=] {company}_sentiment.xlsx already up-to-date.")
