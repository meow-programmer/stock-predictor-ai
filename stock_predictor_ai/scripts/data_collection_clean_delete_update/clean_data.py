import pandas as pd
import os

def clean_data_auto_single(file_path, cleaned_folder):
    """Clean a single CSV file and save to cleaned folder."""
    os.makedirs(cleaned_folder, exist_ok=True)
    df_raw = pd.read_csv(file_path, header=[0,1], parse_dates=[0])
    first_col = df_raw.columns[0]
    df_raw.columns = [
        'Date' if col == first_col else f"{col[0].strip()}_{col[1].strip()}"
        for col in df_raw.columns
    ]
    df_raw['Date'] = pd.to_datetime(df_raw['Date'], errors='coerce')
    df_raw.dropna(subset=['Date'], inplace=True)
    df_raw.sort_values('Date', inplace=True)
    cleaned_file_path = os.path.join(cleaned_folder, os.path.basename(file_path))
    df_raw.to_csv(cleaned_file_path, index=False)
