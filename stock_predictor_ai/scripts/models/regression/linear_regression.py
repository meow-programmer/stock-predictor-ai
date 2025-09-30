import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import timedelta
import os

# --- Setup ---
stock_symbol = input("Enter stock symbol (e.g., ABT): ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.csv')

if not os.path.exists(file_path):
    print("File not found! Available files:", os.listdir(os.path.join(base_dir, 'data', 'cleaned')))
    exit()

# --- Load CSV ---
df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)

close_col = f'Close_{stock_symbol}'
if close_col not in df.columns:
    print(f"Column {close_col} not found in CSV!")
    exit()

# --- SMA Feature ---
df['SMA_50'] = df[close_col].rolling(window=50).mean()
df.dropna(subset=['SMA_50'], inplace=True)
if df.empty:
    print("Not enough data to compute SMA_50.")
    exit()

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

# --- Output ---
print(f"\nMAE: {mae_val:.2f}")
print(f"RMSE: {rmse_val:.2f}")
print(f"Prediction from {latest_date.date()} to {next_week_date.date()}: ${predicted_next:.2f}")
