import pandas as pd
import os

# Ask user if they want to clean all or specific
print("Choose an option:")
print("1. Clean all downloaded raw stock files")
print("2. Clean only a specific stock (manually entered)")

choice = input("Enter 1 or 2: ").strip()

# Define raw/cleaned paths
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
raw_folder = os.path.join(base_path, 'data', 'raw')
cleaned_folder = os.path.join(base_path, 'data', 'cleaned')
os.makedirs(cleaned_folder, exist_ok=True)

# Determine which files to clean
if choice == '1':
    files_to_clean = [f for f in os.listdir(raw_folder) if f.endswith('.csv')]
elif choice == '2':
    ticker = input("Enter stock ticker (e.g., TSLA): ").upper().replace('.', '-')
    files_to_clean = [f"{ticker}.csv"]
else:
    print("Invalid input.")
    exit()

# Clean each file
for file in files_to_clean:
    file_path = os.path.join(raw_folder, file)
    print(f" Cleaning {file}")

    try:
        df_raw = pd.read_csv(file_path, header=[0, 1], parse_dates=[0])

        # Flatten column names
        first_col = df_raw.columns[0]
        df_raw.columns = [
            'Date' if col == first_col else f"{col[0].strip()}_{col[1].strip()}" 
            for col in df_raw.columns
        ]

        # Fix Date column
        df_raw['Date'] = pd.to_datetime(df_raw['Date'], errors='coerce')
        df_raw.dropna(subset=['Date'], inplace=True)
        df_raw.set_index('Date', inplace=True)
        df_raw.sort_index(inplace=True)

        # Drop rows with missing price data
        price_cols = [col for col in df_raw.columns if any(x in col for x in ['Close', 'Open', 'High', 'Low', 'Volume'])]
        df_raw.dropna(subset=price_cols, inplace=True)

        # Drop duplicate dates
        df_raw = df_raw[~df_raw.index.duplicated(keep='first')]

        # Save cleaned file as CSV
        cleaned_path = os.path.join(cleaned_folder, file)
        df_raw.to_csv(cleaned_path, index=True)
        print(f"✅ Cleaned and saved: {file}")

    except Exception as e:
        print(f"❌ Failed to clean {file}: {e}")
