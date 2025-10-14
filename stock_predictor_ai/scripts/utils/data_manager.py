import os
import random
import yfinance as yf
from scripts.data_collection_clean_delete_update.clean_data import clean_data_auto_single

# ----------------------
# GLOBAL FOLDERS
# ----------------------
BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# ----------------------
# FETCH STOCKS
# ----------------------
def fetch_stocks(choice="random_100", ticker=None, num=None, min_num=None, max_num=None, logger=None):
    if logger is None:
        logger = print

    # --- Get S&P500 tickers dynamically ---
    try:
        sp500_tickers = list(yf.Ticker("^GSPC").constituents.keys())
    except:
        sp500_tickers = []  # fallback if yfinance fails

    existing = [f.replace('.csv','') for f in os.listdir(RAW_FOLDER) if f.endswith('.csv')]
    available = [t for t in sp500_tickers if t not in existing]

    # ---------- Choose tickers ----------
    if choice == "single" and ticker:
        tickers_to_download = [ticker]
    elif choice == "random_100":
        tickers_to_download = random.sample(available, min(100, len(available)))
    elif choice == "custom" and num:
        tickers_to_download = random.sample(available, min(num, len(available)))
    elif choice == "range" and min_num and max_num:
        count = max_num - min_num + 1
        tickers_to_download = random.sample(available, min(count, len(available)))
    else:
        tickers_to_download = []

    logger(f"Downloading {len(tickers_to_download)} stocks...")

    # ---------- Download & clean ----------
    for t in tickers_to_download:
        try:
            df = yf.download(t, period="2y")
            if not df.empty:
                raw_file_path = os.path.join(RAW_FOLDER, f"{t}.csv")
                df.to_csv(raw_file_path)
                logger(f"Saved {t} to raw folder.")
                try:
                    clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"Cleaned {t} and saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {t}: {e}")
        except Exception as e:
            logger(f"Failed to download {t}: {e}")

    return {"message": f"{len(tickers_to_download)} stocks downloaded and cleaned successfully."}


# ----------------------
# UPDATE STOCKS
# ----------------------
def update_stocks(logger=None):
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
                try:
                    clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"Cleaned {t} and saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {t}: {e}")
        except Exception as e:
            logger(f"Failed to update {t}: {e}")

    return {"message": f"{len(files)} stocks updated and cleaned successfully."}


# ----------------------
# DELETE STOCKS
# ----------------------
def delete_stocks(tickers=None, random_count=None, logger=None):
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
        if not all_files:
            logger("No CSV files found to delete.")
            return {"message": "No CSV files found to delete."}

        chosen_files = random.sample(all_files, min(random_count, len(all_files)))
        for f in chosen_files:
            for folder in [RAW_FOLDER, CLEANED_FOLDER]:
                file_path = os.path.join(folder, f)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    logger(f"Deleted {file_path}")

    return {"message": f"Deleted {len(deleted_files)} files."}


# ----------------------
# COUNT STOCKS
# ----------------------
def count_stocks():
    raw_files = [f.replace(".csv","") for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]
    cleaned_files = [f.replace(".csv","") for f in os.listdir(CLEANED_FOLDER) if f.endswith(".csv")]
    return {
        "raw_stocks": len(raw_files),
        "cleaned_stocks": len(cleaned_files),
        "raw_tickers": raw_files,
        "cleaned_tickers": cleaned_files
    }