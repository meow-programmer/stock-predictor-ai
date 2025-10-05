import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

def predict_xgb(stock_symbol, n_days=7):
    """
    Predict next n_days closing prices using XGBoost.

    Returns a dictionary:
    {
        "prediction": float (last predicted price),
        "mae": float,
        "rmse": float
    }
    """
    # ==== Paths ====
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.csv')

    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found!")
        return {"prediction": "N/A", "mae": "—", "rmse": "—"}

    # ==== Load Data ====
    data = pd.read_csv(file_path)
    if 'Date' not in data.columns:
        print("❌ Error: 'Date' column not found!")
        return {"prediction": "N/A", "mae": "—", "rmse": "—"}

    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)

    # ==== Detect Close column ====
    close_cols = [c for c in data.columns if 'Close' in c]
    if not close_cols:
        print("❌ Error: No 'Close' column found!")
        return {"prediction": "N/A", "mae": "—", "rmse": "—"}
    close_col = close_cols[0]

    df = data[[close_col]].copy()

    # ==== Feature Engineering ====
    df['SMA'] = df[close_col].rolling(14).mean()
    df['EMA'] = df[close_col].ewm(span=14, adjust=False).mean()
    df['Volatility'] = df[close_col].rolling(14).std()

    delta = df[close_col].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    RS = roll_up / roll_down
    df['RSI'] = 100 - (100 / (1 + RS))

    ema12 = df[close_col].ewm(span=12, adjust=False).mean()
    ema26 = df[close_col].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26

    df['BB_upper'] = df['SMA'] + 2 * df['Volatility']
    df['BB_lower'] = df['SMA'] - 2 * df['Volatility']

    df.dropna(inplace=True)

    if len(df) <= n_days:
        print(f"❌ Not enough data to predict {n_days} days!")
        return {"prediction": "N/A", "mae": "—", "rmse": "—"}

    # ==== Features & Target ====
    X = df.drop(columns=[close_col])
    y = df[close_col]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=n_days, shuffle=False)

    # Scale features
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Predict
    preds = model.predict(X_test_scaled)

    # Compute metrics
    mae_val = mean_absolute_error(y_test, preds)
    rmse_val = np.sqrt(mean_squared_error(y_test, preds))

    # Return last predicted value and metrics
    return {
        "prediction": float(preds[-1]),
        "mae": float(mae_val),
        "rmse": float(rmse_val)
    }
