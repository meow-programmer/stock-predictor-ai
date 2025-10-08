# delete_data.py
import os
import random

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def delete_stocks(random_count=None, tickers=None, logger=None):
    """Delete given or random stocks from raw & cleaned folders."""
    try:
        raw_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith('.csv')]
        cleaned_files = [f for f in os.listdir(CLEANED_FOLDER) if f.endswith('.csv')]
        all_tickers = list(set([f.replace('.csv', '') for f in raw_files + cleaned_files]))

        if tickers:
            to_delete = tickers
        elif random_count:
            to_delete = random.sample(all_tickers, min(random_count, len(all_tickers)))
        else:
            return {"status": "error", "message": "No tickers specified."}

        for t in to_delete:
            for folder in [RAW_FOLDER, CLEANED_FOLDER]:
                path = os.path.join(folder, f"{t}.csv")
                if os.path.exists(path):
                    os.remove(path)
                    if logger:
                        logger(f"[-] Deleted {t} from {folder}")

        return {"status": "success", "message": f"Deleted {len(to_delete)} stock(s): {to_delete}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
