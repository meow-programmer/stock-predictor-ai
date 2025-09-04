import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential  # type:ignore
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt  # For plotting

# Ask for stock symbol
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()

# Build file path relative to this script
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')

if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found!")
    exit()

#  Read stock data
data = pd.read_excel(file_path)

# Dynamically find the closing price column for this stock
close_col = None
for col in data.columns:
    if col.startswith("Close") and stock_symbol in col:
        close_col = col
        break

if close_col is None:
    print(f"Error: Closing price column for {stock_symbol} not found!")
    exit()

# Extract only Close price
prices = data[close_col].values.reshape(-1, 1)

#  Scale data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_prices = scaler.fit_transform(prices)

#  Create sequences for LSTM
seq_length = 60
X, y = [], []
for i in range(seq_length, len(scaled_prices)):
    X.append(scaled_prices[i-seq_length:i])
    y.append(scaled_prices[i])
X, y = np.array(X), np.array(y)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Build LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')

# Train model (short epochs for quick testing)
print("Training LSTM model...")
model.fit(X, y, epochs=20, batch_size=32, verbose=1)

# Predict next 7 days
last_seq = scaled_prices[-seq_length:].reshape(1, seq_length, 1)
next_week_preds = []

current_seq = last_seq.copy()
for _ in range(7):
    pred = model.predict(current_seq)
    next_week_preds.append(pred[0, 0])
    # append predicted value to current sequence
    pred_reshaped = pred.reshape((1, 1, 1))
    current_seq = np.append(current_seq[:, 1:, :], pred_reshaped, axis=1)

# Convert predictions back to original scale
next_week_preds = np.array(next_week_preds).reshape(-1, 1)
next_week_preds = scaler.inverse_transform(next_week_preds)

# Display predictions
print("\nPredicted closing prices for next 7 days:")
for i, price in enumerate(next_week_preds.flatten(), 1):
    print(f"Day {i}: {price:.2f}")

# Plot historical + predicted prices
plt.figure(figsize=(12,6))
plt.plot(prices, label='Actual Prices')
plt.plot(range(len(prices), len(prices)+7), next_week_preds, color='red', marker='o', label='Predicted Prices')
plt.title(f"{stock_symbol} Stock Price Prediction (LSTM)")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.show()


