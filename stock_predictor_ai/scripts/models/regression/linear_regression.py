# linear_regression.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import timedelta
import os

def predict_linear_regression(csv_path):
    """
    Run linear regression on a stock CSV and predict the next week's closing price.

    Parameters
    ----------
    csv_path : str
        Full path to the CSV file (e.g., '.../data/cleaned/AAPL.csv').

    Returns
    -------
    dict
        {
            "prediction": float,
            "latest_date": datetime,
            "next_week_date": datetime,
            "metrics": {
                "MAE": float,
                "RMSE": float
            }
        }
    """
    # --- Load CSV ---
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    stock_symbol = os.path.basename(csv_path).replace(".csv", "")
    close_col = f'Close_{stock_symbol}'

    if close_col not in df.columns:
        raise ValueError(f"Column {close_col} not found in {csv_path}")

    # --- SMA Feature ---
    df['SMA_50'] = df[close_col].rolling(window=50).mean()
    df.dropna(subset=['SMA_50'], inplace=True)
    if df.empty:
        raise ValueError("Not enough data to compute SMA_50.")

    # --- Prepare target ---
    df['Target_Close'] = df[close_col].shift(-7)
    df.dropna(subset=['Target_Close'], inplace=True)

    X = df[['SMA_50']]
    y = df['Target_Close']

    # --- Train Model ---
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # --- Predict next 7 trading days ---
    latest_sma = df.iloc[-1]['SMA_50']
    predicted_next = model.predict([[latest_sma]])[0]

    # --- Next trading date ---
    latest_date = df.iloc[-1]['Date']
    future_days = df[df['Date'] > latest_date]['Date']
    if len(future_days) >= 5:
        next_week_date = future_days.iloc[4]
    else:
        next_week_date = latest_date + timedelta(days=7)

    # --- Metrics ---
    mae_val = mean_absolute_error(y, y_pred)
    rmse_val = np.sqrt(mean_squared_error(y, y_pred))

    return {
        "prediction": predicted_next,
        "latest_date": latest_date,
        "next_week_date": next_week_date,
        "metrics": {
            "MAE": mae_val,
            "RMSE": rmse_val
        }
    }
