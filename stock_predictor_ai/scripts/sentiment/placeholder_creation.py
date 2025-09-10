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
# Update or create sentiment CSVs
# -----------------------------
for file_name in stock_files:
    company = os.path.splitext(file_name)[0]
    stock_file = os.path.join(CLEANED_FOLDER, file_name)
    sentiment_file = os.path.join(SENTIMENT_FOLDER, f'{company}_sentiment.csv')

    # Read stock file
    try:
        if file_name.endswith('.xlsx'):
            df_stock = pd.read_excel(stock_file, parse_dates=['Date'], engine='openpyxl')
        else:
            df_stock = pd.read_csv(stock_file, parse_dates=['Date'])
    except Exception as e:
        print(f"[!] Skipping {company}: cannot read file ({e})")
        continue

    # Create or update sentiment file
    if os.path.exists(sentiment_file):
        df_sentiment = pd.read_csv(sentiment_file, parse_dates=['Date'])
        last_date = df_sentiment['Date'].max()
        # Get new dates after last date
        new_dates = df_stock[df_stock['Date'] > last_date]['Date']
        # Ensure today's date is included
        if today > last_date and today not in new_dates.values:
            new_dates = pd.concat([new_dates, pd.Series([today])])
        if not new_dates.empty:
            new_rows = pd.DataFrame({'Date': new_dates, 'Sentiment': 0.0})
            df_sentiment = pd.concat([df_sentiment, new_rows], ignore_index=True)
            df_sentiment = df_sentiment.sort_values('Date').reset_index(drop=True)
            df_sentiment.to_csv(sentiment_file, index=False)
            print(f"[+] Updated {company}_sentiment.csv with {len(new_rows)} new dates.")
        else:
            print(f"[=] {company}_sentiment.csv already up-to-date.")
    else:
        # Create new sentiment CSV starting from stock file dates
        stock_dates = df_stock['Date']
        if today not in stock_dates.values:
            stock_dates = pd.concat([stock_dates, pd.Series([today])])
        sentiment_df = pd.DataFrame({'Date': stock_dates, 'Sentiment': 0.0})
        sentiment_df = sentiment_df.sort_values('Date').reset_index(drop=True)
        sentiment_df.to_csv(sentiment_file, index=False)
        print(f"[+] Created sentiment CSV for {company}, {len(sentiment_df)} rows.")
