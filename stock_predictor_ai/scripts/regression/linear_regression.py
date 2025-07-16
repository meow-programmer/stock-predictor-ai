import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from datetime import timedelta

# ==== Path Setup ====
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')
df_full = pd.read_excel(file_path)

# ==== Feature Engineering ====
df_full['Date'] = pd.to_datetime(df_full['Date'])
df_full.sort_values('Date', inplace=True)
df_full['SMA_50'] = df_full[f'Close_{stock_symbol}'].rolling(window=50).mean()
df_full.dropna(subset=['SMA_50'], inplace=True)

# ==== Save actual last trading day before dropping for training ====
actual_latest_row = df_full.iloc[-1]
actual_latest_date = actual_latest_row['Date']
actual_latest_sma = actual_latest_row['SMA_50']

# ==== Prepare training data (with shifted target) ====
df = df_full.copy()
df['Target_Close'] = df[f'Close_{stock_symbol}'].shift(-7)
df.dropna(subset=['Target_Close'], inplace=True)

x = df[['SMA_50']]
y = df['Target_Close']
model = LinearRegression()
model.fit(x, y)
y_pred = model.predict(x)

# ==== Metric Functions ====
def mae(y_true, y_pred): return mean_absolute_error(y_true, y_pred)
def mse(y_true, y_pred): return mean_squared_error(y_true, y_pred)
def rmse(y_true, y_pred): return np.sqrt(mse(y_true, y_pred))
def adjusted_r2(y_true, y_pred, x):
    r2 = model.score(x, y_true)
    n, k = x.shape
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)
def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true - y_pred
    small = np.abs(error) <= delta
    squared = 0.5 * error ** 2
    linear = delta * (np.abs(error) - 0.5 * delta)
    return np.mean(np.where(small, squared, linear))

# ==== Predict Next Week from Actual Latest Row ====
next_week_pred = model.predict(np.array([[actual_latest_sma]]))[0]

# Try to get a real trading date after 7 days
future_trading_days = df_full[df_full['Date'] > actual_latest_date]['Date']
if len(future_trading_days) >= 5:
    next_week_date = future_trading_days.iloc[4]  # 5th trading day after latest
else:
    next_week_date = actual_latest_date + timedelta(days=7)  # fallback

# ==== Output ====
print("\nEvaluation Metrics (Full Set)")
print("----------------------------")
print(f"MAE: {mae(y, y_pred):.2f}")
print(f"MSE: {mse(y, y_pred):.2f}")
print(f"RMSE: {rmse(y, y_pred):.2f}")
print(f"Adjusted R²: {adjusted_r2(y, y_pred, x):.4f}")
print(f"Huber Loss: {huber_loss(y, y_pred):.2f}")

print("\n📈 Predicted Closing Price")
print("----------------------------")
print(f"From: {actual_latest_date.date()}  -->  To: {next_week_date.date()}  |  Predicted Close: ${next_week_pred:.2f}")
