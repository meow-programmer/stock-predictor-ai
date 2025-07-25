import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from datetime import timedelta
from ta.momentum import RSIIndicator #RSI
from ta.trend import MACD #MACD
from ta.volatility import BollingerBands #BB

# ==== Path Setup ====
base_dir = os.path.abspath(os.path.join(os.getcwd(), 'stock_predictor_ai'))
file_path = os.path.join(base_dir, 'data', 'cleaned')
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
stock_file = os.path.join(file_path, f'{stock_symbol}.xlsx')
df = pd.read_excel(stock_file)

# ==== Preprocessing ====
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Save original DataFrame to preserve last row
original_df = df.copy()

# Feature Engineering
df['SMA_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).mean()
df['SMA_20'] = df[f'Close_{stock_symbol}'].rolling(window=20).mean()
df['Volatility_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).std()

# RSI
rsi = RSIIndicator(close=df[f'Close_{stock_symbol}'], window=14)
df["RSI_14"] = rsi.rsi()

# MACD
macd = MACD(close=df[f'Close_{stock_symbol}'])
df["MACD"] = macd.macd()
df["MACD_Signal"] = macd.macd_signal()
df["MACD_Diff"] = df["MACD"] - df["MACD_Signal"]

# Bollinger Bands
bb = BollingerBands(close=df[f'Close_{stock_symbol}'], window=20, window_dev=2)
df["BB_Upper"] = bb.bollinger_hband()
df["BB_Lower"] = bb.bollinger_lband()
df["BB_Width"] = df["BB_Upper"] - df["BB_Lower"]


# Predict the close price 5 business days ahead
df['Target_Close'] = df[f'Close_{stock_symbol}'].shift(-5)
features = [
    'SMA_10', 'SMA_20', 'Volatility_10',
    'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Diff',
    'BB_Upper', 'BB_Lower', 'BB_Width'
]

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
# Take the last 50 rows to be safe (so all rolling windows work)
latest_valid = original_df.tail(50).copy()

# Basic indicators
latest_valid['SMA_10'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=10).mean()
latest_valid['SMA_20'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=20).mean()
latest_valid['Volatility_10'] = latest_valid[f'Close_{stock_symbol}'].rolling(window=10).std()

# RSI
rsi = RSIIndicator(close=latest_valid[f'Close_{stock_symbol}'], window=14)
latest_valid['RSI_14'] = rsi.rsi()

# MACD
macd = MACD(close=latest_valid[f'Close_{stock_symbol}'])
latest_valid['MACD'] = macd.macd()
latest_valid['MACD_Signal'] = macd.macd_signal()
latest_valid['MACD_Diff'] = macd.macd_diff()

# Bollinger Bands
bb = BollingerBands(close=latest_valid[f'Close_{stock_symbol}'], window=20, window_dev=2)
latest_valid['BB_Upper'] = bb.bollinger_hband()
latest_valid['BB_Lower'] = bb.bollinger_lband()
latest_valid['BB_Width'] = latest_valid['BB_Upper'] - latest_valid['BB_Lower']

# Drop NaNs caused by rolling indicators
latest_valid.dropna(inplace=True)

# Now select the latest row for prediction
latest_features_row = latest_valid.iloc[-1]
latest_features = latest_features_row[features].values.reshape(1, -1)


# Now get the real most recent available feature row ----> important
latest_features_row = latest_valid.iloc[-1]
latest_features = latest_features_row[features].values.reshape(1, -1)
latest_date = latest_features_row['Date']

# ==== Predict Next Week ====
predicted_price = model.predict(latest_features)[0]

# Calculate next trading week date (just skip weekends)
next_week_date = latest_date
days_added = 0
while days_added < 5:
    next_week_date += timedelta(days=1)
    if next_week_date.weekday() < 5:
        days_added += 1

# ==== Print Output ====
print("\n📊 Latest Technical Indicators")
print("-----------------------------")
print(f"RSI (14): {latest_features_row['RSI_14']:.2f}")
print(f"MACD: {latest_features_row['MACD']:.2f}")
print(f"MACD Signal: {latest_features_row['MACD_Signal']:.2f}")
print(f"Bollinger Upper: {latest_features_row['BB_Upper']:.2f}")
print(f"Bollinger Lower: {latest_features_row['BB_Lower']:.2f}")


print("\n📈 Predicted Closing Price")
print("----------------------------")
print(f"From: {latest_date.date()}  -->  To: {next_week_date.date()}  |  Predicted Close: ${predicted_price:.2f}")