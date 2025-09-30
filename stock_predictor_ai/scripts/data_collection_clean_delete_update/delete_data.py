import os
import random

# -----------------------------
# Base directories
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_FOLDER = os.path.join(BASE_DIR, 'data', 'raw')
CLEAN_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')

# -----------------------------
# Ask user if they want to delete random stocks
# -----------------------------
delete_random = input("Do you want to delete random tickers? (y/n): ").strip().lower()

# Get all tickers currently in raw folder (CSV or XLSX)
existing_files = [f for f in os.listdir(RAW_FOLDER) if f.endswith((".csv", ".xlsx"))]
existing_tickers = [os.path.splitext(f)[0] for f in existing_files]

if delete_random == "y":
    try:
        n = int(input(f"How many random tickers do you want to delete? (1-{len(existing_tickers)}): ").strip())
        if n > 0 and n <= len(existing_tickers):
            random_tickers = random.sample(existing_tickers, n)
            print(f"[!] Randomly deleting {n} tickers: {random_tickers}")

            # Remove files from raw and cleaned folders (check both .csv and .xlsx)
            for ticker in random_tickers:
                for folder in [RAW_FOLDER, CLEAN_FOLDER]:
                    for ext in [".csv", ".xlsx"]:
                        file_path = os.path.join(folder, f"{ticker}{ext}")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[+] Removed {file_path}")

        else:
            print(f"[!] Invalid number. Must be between 1 and {len(existing_tickers)}")
    except ValueError:
        print("[!] Invalid input. Skipping random delete.")
else:
    print("[=] No tickers deleted.")
