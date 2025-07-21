import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from datetime import timedelta

# ==== Path Setup ====
base_dir = os.path.abspath(os.path.join(os.getcwd(), 'stock_predictor_ai'))
file_path = os.path.join(base_dir, 'data', 'cleaned')
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
stock_file = os.path.join(file_path, f'{stock_symbol}.xlsx')
df = pd.read_excel(stock_file)

# ==== Preprocessing ====
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
original_df = df.copy()

# ==== Feature Engineering ====
close_col = f'Close_{stock_symbol}'
df['SMA_10'] = df[close_col].rolling(window=10).mean()
df['SMA_20'] = df[close_col].rolling(window=20).mean()
df['Volatility_10'] = df[close_col].rolling(window=10).std()

# --- RSI (14-day) ---
delta = df[close_col].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
df['RSI_14'] = 100 - (100 / (1 + rs))

# --- MACD ---
ema_12 = df[close_col].ewm(span=12, adjust=False).mean()
ema_26 = df[close_col].ewm(span=26, adjust=False).mean()
df['MACD'] = ema_12 - ema_26
# Optional: df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

# --- Bollinger Band Width (difference between upper and lower bands) ---
sma_20 = df[close_col].rolling(window=20).mean()
std_20 = df[close_col].rolling(window=20).std()
df['Bollinger_Width'] = (2 * std_20) * 2  # Upper - Lower

# --- Prediction Target ---
df['Target_Close'] = df[close_col].shift(-5)

# --- Final Features ---
features = ['SMA_10', 'SMA_20', 'Volatility_10', 'RSI_14', 'MACD', 'Bollinger_Width']
df.dropna(inplace=True)

# ==== Train/Test Split ====
x = df[features]
y = df['Target_Close']
split_point = int(len(df) * 0.8)
x_train, x_test = x[:split_point], x[split_point:]
y_train, y_test = y[:split_point], y[split_point:]

# ==== Train Model ====
model = LinearRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

# ==== Evaluation ====
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = model.score(x_test, y_test)

# ==== Get Latest Available Features ====
latest_valid = original_df.tail(60).copy()  # Get enough rows for all indicators
latest_valid['SMA_10'] = latest_valid[close_col].rolling(window=10).mean()
latest_valid['SMA_20'] = latest_valid[close_col].rolling(window=20).mean()
latest_valid['Volatility_10'] = latest_valid[close_col].rolling(window=10).std()

delta = latest_valid[close_col].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
latest_valid['RSI_14'] = 100 - (100 / (1 + rs))

ema_12 = latest_valid[close_col].ewm(span=12, adjust=False).mean()
ema_26 = latest_valid[close_col].ewm(span=26, adjust=False).mean()
latest_valid['MACD'] = ema_12 - ema_26

sma_20 = latest_valid[close_col].rolling(window=20).mean()
std_20 = latest_valid[close_col].rolling(window=20).std()
latest_valid['Bollinger_Width'] = (2 * std_20) * 2

latest_valid.dropna(inplace=True)
latest_features_row = latest_valid.iloc[-1]
latest_features = latest_features_row[features].values.reshape(1, -1)
latest_date = latest_features_row['Date']

# ==== Predict Next Week ====
predicted_price = model.predict(latest_features)[0]

# ==== Get Future Date (Skip Weekends) ====
next_week_date = latest_date
days_added = 0
while days_added < 5:
    next_week_date += timedelta(days=1)
    if next_week_date.weekday() < 5:
        days_added += 1

# ==== Output ====
print("\nEvaluation Metrics (Test Set)")
print("----------------------------")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.4f}")

print("\n📈 Predicted Closing Price")
print("----------------------------")
print(f"From: {latest_date.date()}  -->  To: {next_week_date.date()}  |  Predicted Close: ${predicted_price:.2f}")
