import os
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

def predict_multiple_regression(stock_symbol):
    """
    Run multiple regression using various technical indicators to predict next week's closing price.

    Parameters
    ----------
    stock_symbol : str
        Stock symbol (e.g., 'AAPL')

    Returns
    -------
    dict
        {
            "prediction": float,
            "mae": float,
            "rmse": float,
            "latest_date": str,
            "next_week_date": str
        }
    """
    # === Setup Paths ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned')
    csv_path = os.path.join(cleaned_path, f'{stock_symbol}.csv')

    if not os.path.exists(csv_path):
        return {"error": f"File not found: {csv_path}"}

    # === Load Data ===
    df = pd.read_csv(csv_path)
    if f'Close_{stock_symbol}' not in df.columns:
        return {"error": f"Column Close_{stock_symbol} not found in file."}

    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    original_df = df.copy()

    # === Feature Engineering ===
    df['SMA_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).mean()
    df['SMA_20'] = df[f'Close_{stock_symbol}'].rolling(window=20).mean()
    df['Volatility_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).std()

    rsi = RSIIndicator(close=df[f'Close_{stock_symbol}'], window=14)
    df["RSI_14"] = rsi.rsi()

    macd = MACD(close=df[f'Close_{stock_symbol}'])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Diff"] = df["MACD"] - df["MACD_Signal"]

    bb = BollingerBands(close=df[f'Close_{stock_symbol}'], window=20, window_dev=2)
    df["BB_Upper"] = bb.bollinger_hband()
    df["BB_Lower"] = bb.bollinger_lband()
    df["BB_Width"] = df["BB_Upper"] - df["BB_Lower"]

    df['Target_Close'] = df[f'Close_{stock_symbol}'].shift(-5)

    features = [
        'SMA_10', 'SMA_20', 'Volatility_10',
        'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Diff',
        'BB_Upper', 'BB_Lower', 'BB_Width'
    ]
    df.dropna(inplace=True)

    if df.empty:
        return {"error": "Not enough data after feature engineering."}

    # === Train-Test Split ===
    X = df[features]
    y = df['Target_Close']
    split_point = int(len(df) * 0.8)
    X_train, X_test = X[:split_point], X[split_point:]
    y_train, y_test = y[:split_point], y[split_point:]

    # === Train Model ===
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # === Predict next week ===
    latest_valid = original_df.tail(50).copy()
    latest_valid['SMA_10'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=10).mean()
    latest_valid['SMA_20'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=20).mean()
    latest_valid['Volatility_10'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=10).std()

    rsi = RSIIndicator(close=latest_valid[f'Close_{stock_symbol}'], window=14)
    latest_valid['RSI_14'] = rsi.rsi()

    macd = MACD(close=latest_valid[f'Close_{stock_symbol}'])
    latest_valid['MACD'] = macd.macd()
    latest_valid['MACD_Signal'] = macd.macd_signal()
    latest_valid['MACD_Diff'] = latest_valid['MACD'] - latest_valid['MACD_Signal']

    bb = BollingerBands(close=latest_valid[f'Close_{stock_symbol}'], window=20, window_dev=2)
    latest_valid['BB_Upper'] = bb.bollinger_hband()
    latest_valid['BB_Lower'] = bb.bollinger_lband()
    latest_valid['BB_Width'] = latest_valid['BB_Upper'] - latest_valid['BB_Lower']

    latest_valid.dropna(inplace=True)
    if latest_valid.empty:
        return {"error": "Not enough recent data for prediction."}

    latest_row = latest_valid.iloc[-1]
    latest_features = latest_row[features].values.reshape(1, -1)
    latest_date = latest_row['Date']

    predicted_price = model.predict(latest_features)[0]

    # === Calculate Next Business Week Date ===
    next_week_date = latest_date
    days_added = 0
    while days_added < 5:
        next_week_date += timedelta(days=1)
        if next_week_date.weekday() < 5:
            days_added += 1

    # === Evaluation Metrics ===
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # === Return Output ===
    return {
        "prediction": round(float(predicted_price), 2),
        "mae": round(float(mae), 3),
        "rmse": round(float(rmse), 3),
        "latest_date": str(latest_date.date()),
        "next_week_date": str(next_week_date.date())
    }
