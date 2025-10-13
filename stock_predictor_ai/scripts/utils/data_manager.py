import os
import random
import yfinance as yf
import pandas as pd
import requests
from scripts.data_collection_clean_delete_update.clean_data import clean_data_auto_single

# ----------------------
# UTILITY PATHS
# ----------------------
def get_folders(raw_folder=None, cleaned_folder=None):
    base_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
    RAW_FOLDER = raw_folder or os.path.join(base_dir, 'data', 'raw')
    CLEANED_FOLDER = cleaned_folder or os.path.join(base_dir, 'data', 'cleaned')
    os.makedirs(RAW_FOLDER, exist_ok=True)
    os.makedirs(CLEANED_FOLDER, exist_ok=True)
    return RAW_FOLDER, CLEANED_FOLDER


# ----------------------
# GET S&P 500 TICKERS
# ----------------------
def get_sp500_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_df = pd.read_html(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text)[0]
        tickers = [t.replace('.', '-') for t in sp500_df['Symbol'].tolist()]
        return tickers
    except Exception as e:
        print(f"⚠️ Failed to fetch S&P 500 tickers dynamically: {e}")
        # fallback: minimal list just in case
        return ["AAPL","MSFT","GOOGL","AMZN","TSLA","FB","BRK-B"]


# ----------------------
# FETCH STOCKS
# ----------------------
def fetch_stocks(choice="random_100", ticker=None, num=None, min_num=None, max_num=None,
                 raw_folder=None, cleaned_folder=None, logger=None):

    RAW_FOLDER, CLEANED_FOLDER = get_folders(raw_folder, cleaned_folder)
    logger = logger or print

    sp500_tickers = get_sp500_tickers()

    # Already cleaned stocks
    existing_cleaned = [f.replace(".csv","") for f in os.listdir(CLEANED_FOLDER) if f.endswith(".csv")]

    # Available for random/custom/range
    available = [t for t in sp500_tickers if t not in existing_cleaned]

    # ---------- CHOOSE TICKERS ----------
    if choice == "single" and ticker:
        tickers_to_download = [ticker]
    elif choice == "random_100":
        tickers_to_download = random.sample(available, min(100, len(available)))
    elif choice == "custom" and num:
        tickers_to_download = random.sample(available, min(num, len(available)))
    elif choice == "range" and min_num and max_num:
        # Always download exactly max_num stocks (or as many as available)
        tickers_to_download = random.sample(available, min(max_num, len(available)))
    else:
        tickers_to_download = []


    if not tickers_to_download:
        logger("⚠️ No tickers available to download.")
        return {"message": "No stocks downloaded."}

    logger(f"Downloading {len(tickers_to_download)} stocks...")

    # ---------- DOWNLOAD & CLEAN ----------
    for t in tickers_to_download:
        try:
            df = yf.download(t, period="2y")
            if not df.empty:
                raw_file_path = os.path.join(RAW_FOLDER, f"{t}.csv")
                df.to_csv(raw_file_path)
                logger(f"[RAW] Saved {t}.")

                try:
                    clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"[CLEANED] {t} saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {t}: {e}")
            else:
                logger(f"⚠️ No data for {t}. Skipping.")
        except Exception as e:
            logger(f"❌ Download failed for {t}: {e}")

    return {"message": f"{len(tickers_to_download)} stocks downloaded and cleaned successfully."}


# ----------------------
# UPDATE STOCKS
# ----------------------
def update_stocks(raw_folder=None, cleaned_folder=None, logger=None):
    RAW_FOLDER, CLEANED_FOLDER = get_folders(raw_folder, cleaned_folder)
    logger = logger or print

    files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]
    if not files:
        return {"message": "No raw CSV files found to update."}

    for idx, f in enumerate(files, start=1):
        ticker = f.replace(".csv","")
        raw_file_path = os.path.join(RAW_FOLDER, f)
        try:
            df = yf.download(ticker, period="2y")
            if not df.empty:
                df.to_csv(raw_file_path)
                logger(f"[RAW] Updated {ticker} ({idx}/{len(files)})")

                try:
                    clean_data_auto_single(raw_file_path, CLEANED_FOLDER)
                    logger(f"[CLEANED] {ticker} saved to cleaned folder.")
                except Exception as e:
                    logger(f"❌ Cleaning failed for {ticker}: {e}")
            else:
                logger(f"⚠️ No data for {ticker}. Skipping.")
        except Exception as e:
            logger(f"❌ Update failed for {ticker}: {e}")

    return {"message": f"{len(files)} stocks updated and cleaned successfully."}


# ----------------------
# DELETE STOCKS
# ----------------------
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

    # --- DELETE BY TICKERS ---
    if tickers:
        chosen_files = tickers
    # --- DELETE RANDOM COUNT ---
    elif random_count:
        all_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")]
        if not all_files:
            logger("No CSV files found to delete.")
            return {"message": "No CSV files found to delete."}
        chosen_files = random.sample(all_files, min(random_count, len(all_files)))
    else:
        return {"message": "No tickers or random count specified for deletion."}

    # --- DELETE FILES ---
    for f in chosen_files:
        for folder in [RAW_FOLDER, CLEANED_FOLDER]:
            file_path = os.path.join(folder, f if f.endswith('.csv') else f"{f}.csv")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger(f"Deleted {file_path}")
        deleted_files.append(f)  # append **once per ticker/file**, not per folder

    return {"message": f"Deleted {len(deleted_files)} files."}

