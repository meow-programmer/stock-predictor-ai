import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

def predict_lstm(stock_symbol):
    """
    Trains a simple LSTM model and returns predictions + metrics for the given stock.
    """

    # === File path ===
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.csv')

    if not os.path.exists(file_path):
        return {"error": f"File '{file_path}' not found!"}

    # === Read stock data ===
    data = pd.read_csv(file_path)

    # Find Close column dynamically
    close_col = None
    for col in data.columns:
        if col.startswith("Close") and stock_symbol in col:
            close_col = col
            break

    if close_col is None:
        return {"error": f"Closing price column for {stock_symbol} not found!"}

    # === Prepare Data ===
    prices = data[close_col].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    seq_length = 60
    X, y = [], []
    for i in range(seq_length, len(scaled_prices)):
        X.append(scaled_prices[i-seq_length:i])
        y.append(scaled_prices[i])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    # === Build LSTM model ===
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    # === Train model ===
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)  # keep short for testing

    # === Predict next 7 days ===
    last_seq = scaled_prices[-seq_length:].reshape(1, seq_length, 1)
    next_week_preds = []
    current_seq = last_seq.copy()

    for _ in range(7):
        pred = model.predict(current_seq, verbose=0)
        next_week_preds.append(pred[0, 0])
        current_seq = np.append(current_seq[:, 1:, :], pred.reshape(1, 1, 1), axis=1)

    next_week_preds = np.array(next_week_preds).reshape(-1, 1)
    next_week_preds = scaler.inverse_transform(next_week_preds)

    # === Compute metrics on training ===
    preds_train = model.predict(X, verbose=0)
    preds_train = scaler.inverse_transform(preds_train)
    y_true = scaler.inverse_transform(y)

    mae = mean_absolute_error(y_true, preds_train)
    rmse = math.sqrt(mean_squared_error(y_true, preds_train))

    # === Return structured data ===
    return {
        "prediction": float(next_week_preds[-1][0]),  # last day’s predicted price
        "next_7_days": next_week_preds.flatten().tolist(),
        "mae": round(mae, 3),
        "rmse": round(rmse, 3)
    }
