import os
import pandas as pd
from datetime import datetime, timedelta

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

    # Determine last date in sentiment file or start from first stock date
    if os.path.exists(sentiment_file):
        df_sentiment = pd.read_csv(sentiment_file, parse_dates=['Date'])
        last_date = df_sentiment['Date'].max()
    else:
        df_sentiment = pd.DataFrame(columns=['Date', 'Sentiment'])
        last_date = df_stock['Date'].min() - timedelta(days=1)  # start one day before first stock date

    # Generate all consecutive dates from last_date+1 to today
    start_date = last_date + timedelta(days=1)
    if start_date <= today:
        all_new_dates = pd.date_range(start=start_date, end=today, freq='D')
        new_rows = pd.DataFrame({'Date': all_new_dates, 'Sentiment': 0.0})
        df_sentiment = pd.concat([df_sentiment, new_rows], ignore_index=True)
        df_sentiment = df_sentiment.sort_values('Date').reset_index(drop=True)
        df_sentiment.to_csv(sentiment_file, index=False)
        print(f"[+] {company}_sentiment.csv updated with {len(new_rows)} new dates.")
    else:
        print(f"[=] {company}_sentiment.csv already up-to-date.")
