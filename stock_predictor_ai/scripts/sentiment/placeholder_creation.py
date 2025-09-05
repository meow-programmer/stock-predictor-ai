import os
import pandas as pd

# 1️⃣ Locate all stock files
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
cleaned_folder = os.path.join(base_dir, 'data', 'cleaned')
sentiment_folder = os.path.join(base_dir, 'data', 'company_sentiment_ready')
os.makedirs(sentiment_folder, exist_ok=True)

# Accept both Excel and CSV stock files
stock_files = [f for f in os.listdir(cleaned_folder) if f.endswith(('.xlsx', '.csv'))]
company_files = [f.split('.')[0] for f in stock_files]

print("Detected companies:", company_files)

# 2️⃣ Generate or update placeholder sentiment
for file_name in stock_files:
    company = file_name.split('.')[0]
    stock_file = os.path.join(cleaned_folder, file_name)
    save_path = os.path.join(sentiment_folder, f'{company}_sentiment.csv')

    # Read stock file
    try:
        if file_name.endswith('.xlsx'):
            df_stock = pd.read_excel(stock_file, parse_dates=['Date'], engine='openpyxl')
        else:
            df_stock = pd.read_csv(stock_file, parse_dates=['Date'])
    except Exception as e:
        print(f"Skipping {company}: cannot read file ({e})")
        continue

    # Read existing sentiment if exists
    if os.path.exists(save_path):
        df_sentiment = pd.read_csv(save_path, parse_dates=['Date'])
        # Find new dates that are in stock data but not in sentiment CSV
        new_dates = df_stock[~df_stock['Date'].isin(df_sentiment['Date'])]['Date']
        if not new_dates.empty:
            new_rows = pd.DataFrame({'Date': new_dates, 'Sentiment': 0.0})
            df_sentiment = pd.concat([df_sentiment, new_rows], ignore_index=True)
            df_sentiment = df_sentiment.sort_values('Date').reset_index(drop=True)
            df_sentiment.to_csv(save_path, index=False)
            print(f"Updated {company}_sentiment.csv with {len(new_rows)} new dates.")
        else:
            print(f"{company}_sentiment.csv already up-to-date.")
    else:
        # Create new sentiment CSV
        sentiment_df = pd.DataFrame({
            'Date': df_stock['Date'],
            'Sentiment': 0.0
        })
        sentiment_df.to_csv(save_path, index=False)
        print(f"Created new placeholder sentiment CSV for {company}, {len(sentiment_df)} rows.")
