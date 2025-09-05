import os
import pandas as pd

# 1️⃣ Locate all stock files
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
cleaned_folder = os.path.join(base_dir, 'data', 'cleaned')

# Accept both Excel and CSV stock files
stock_files = [f for f in os.listdir(cleaned_folder) if f.endswith(('.xlsx', '.csv'))]
company_files = [f.split('.')[0] for f in stock_files]  # get company symbol

print("Detected companies:", company_files)

# 2️⃣ Create folder for sentiment CSVs
sentiment_folder = os.path.join(base_dir, 'data', 'company_sentiment_ready')
os.makedirs(sentiment_folder, exist_ok=True)

# 3️⃣ Generate placeholder sentiment
for file_name in stock_files:
    company = file_name.split('.')[0]
    stock_file = os.path.join(cleaned_folder, file_name)

    try:
        if file_name.endswith('.xlsx'):
            df_stock = pd.read_excel(stock_file, parse_dates=['Date'], engine='openpyxl')
        else:  # CSV
            df_stock = pd.read_csv(stock_file, parse_dates=['Date'])
    except Exception as e:
        print(f"Skipping {company}: cannot read file ({e})")
        continue

    # Placeholder sentiment (all zeros)
    sentiment_df = pd.DataFrame({
        'Date': df_stock['Date'],
        'Sentiment': 0.0
    })

    # Save sentiment CSV
    save_path = os.path.join(sentiment_folder, f'{company}_sentiment.csv')
    sentiment_df.to_csv(save_path, index=False)
    print(f"Placeholder sentiment CSV created for {company}, {len(sentiment_df)} rows.")
