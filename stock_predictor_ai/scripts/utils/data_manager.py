import os
import pandas as pd
import random
from datetime import datetime
import yfinance as yf  
from scripts.data_collection_clean_delete_update import clean_data 

# ----------------------
# FETCH STOCKS
# ----------------------
def fetch_stocks(choice="random_100", ticker=None, num=None, min_num=None, max_num=None,
                 raw_folder=None, cleaned_folder=None, logger=None):
    
    RAW_FOLDER = raw_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'raw')
    CLEANED_FOLDER = cleaned_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'cleaned')
    os.makedirs(RAW_FOLDER, exist_ok=True)
    os.makedirs(CLEANED_FOLDER, exist_ok=True)

    if logger is None:
        logger = print

    # Determine tickers to download
    tickers_list = []
    all_tickers = ['AAPL','TSLA','MSFT','GOOGL','AMZN','NVDA','META','NFLX','INTC','AMD']

    if choice == "random_100":
        tickers_list = random.sample(all_tickers, min(100, len(all_tickers)))
    elif choice == "single" and ticker:
        tickers_list = [ticker]
    elif choice == "custom" and num:
        tickers_list = random.sample(all_tickers, min(num, len(all_tickers)))
    elif choice == "range" and min_num and max_num:
        count = random.randint(min_num, max_num)
        tickers_list = random.sample(all_tickers, min(count, len(all_tickers)))

    logger(f"Downloading {len(tickers_list)} stocks...")

    # Download & save raw + auto-clean
    for t in tickers_list:
        try:
            df = yf.download(t, period="2y")
            if not df.empty:
                raw_file_path = os.path.join(RAW_FOLDER, f"{t}.csv")
                df.to_csv(raw_file_path)
                logger(f"Saved {t} to raw folder.")

                # --- Auto-clean ---
                try:
                    clean_data.clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"Cleaned {t} and saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {t}: {e}")

        except Exception as e:
            logger(f"Failed to download {t}: {e}")

    return {"message": f"{len(tickers_list)} stocks downloaded and cleaned successfully."}


# ----------------------
# UPDATE STOCKS
# ----------------------
def update_stocks(raw_folder=None, cleaned_folder=None, logger=None):
    RAW_FOLDER = raw_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'raw')
    CLEANED_FOLDER = cleaned_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'cleaned')
    os.makedirs(RAW_FOLDER, exist_ok=True)
    os.makedirs(CLEANED_FOLDER, exist_ok=True)

    if logger is None:
        logger = print

    files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]
    if not files:
        return {"message": "No raw CSV files found to update."}

    for f in files:
        t = f.replace(".csv", "")
        try:
            df = yf.download(t, period="2y")
            if not df.empty:
                raw_file_path = os.path.join(RAW_FOLDER, f)
                df.to_csv(raw_file_path)
                logger(f"Updated {t} in raw folder.")

                # --- Auto-clean ---
                try:
                    clean_data.clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"Cleaned {t} and saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {t}: {e}")

        except Exception as e:
            logger(f"Failed to update {t}: {e}")

    return {"message": f"{len(files)} stocks updated and cleaned successfully."}


# ----------------------
# DELETE STOCKS
# ----------------------
def delete_stocks(tickers=None, random_count=None, raw_folder=None, cleaned_folder=None, logger=None):
    RAW_FOLDER = raw_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'raw')
    CLEANED_FOLDER = cleaned_folder or os.path.join(os.path.abspath(os.path.join(__file__, '..', '..', '..')), 'data', 'cleaned')
    os.makedirs(RAW_FOLDER, exist_ok=True)
    os.makedirs(CLEANED_FOLDER, exist_ok=True)

    if logger is None:
        logger = print

    deleted_files = []

    # Delete by tickers
    if tickers:
        for t in tickers:
            for folder in [RAW_FOLDER, CLEANED_FOLDER]:
                file_path = os.path.join(folder, f"{t}.csv")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logger(f"Deleted {file_path}")

    # Delete random count
    elif random_count:
        all_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]
        chosen_files = random.sample(all_files, min(random_count, len(all_files)))
        for f in chosen_files:
            for folder in [RAW_FOLDER, CLEANED_FOLDER]:
                file_path = os.path.join(folder, f)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logger(f"Deleted {file_path}")

    return {"message": f"Deleted {len(deleted_files)} files."}
