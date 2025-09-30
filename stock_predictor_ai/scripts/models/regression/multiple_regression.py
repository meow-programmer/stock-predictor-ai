import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from datetime import timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

# ==== Path Setup ====
base_dir = os.path.abspath(os.path.join(os.getcwd(), 'stock_predictor_ai'))
file_path = os.path.join(base_dir, 'data', 'cleaned')
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
stock_file = os.path.join(file_path, f'{stock_symbol}.csv')
df = pd.read_csv(stock_file)

# ==== Preprocessing ====
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
original_df = df.copy()

# Feature Engineering
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

# Predict the close price 5 business days ahead
df['Target_Close'] = df[f'Close_{stock_symbol}'].shift(-5)
features = ['SMA_10','SMA_20','Volatility_10','RSI_14','MACD','MACD_Signal','MACD_Diff','BB_Upper','BB_Lower','BB_Width']
df.dropna(inplace=True)

# Train/Test Split
x = df[features]
y = df['Target_Close']
split_point = int(len(df) * 0.8)
x_train, x_test = x[:split_point], x[split_point:]
y_train, y_test = y[:split_point], y[split_point:]

model = LinearRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_test)

# Latest feature row for prediction
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
latest_features_row = latest_valid.iloc[-1]
latest_features = latest_features_row[features].values.reshape(1, -1)
latest_date = latest_features_row['Date']

# Predict
predicted_price = model.predict(latest_features)[0]

# Next week date
next_week_date = latest_date
days_added = 0
while days_added < 5:
    next_week_date += timedelta(days=1)
    if next_week_date.weekday() < 5:
        days_added += 1

# ==== Save to CSV ====
output_file = os.path.join(base_dir, 'data', 'predictions', f'{stock_symbol}_prediction.csv')
os.makedirs(os.path.dirname(output_file), exist_ok=True)

output_df = pd.DataFrame([{
    'Stock': stock_symbol,
    'Date': latest_date.date(),
    'Predicted_Date': next_week_date.date(),
    'Predicted_Close': predicted_price,
    'RSI_14': latest_features_row['RSI_14'],
    'MACD': latest_features_row['MACD'],
    'MACD_Signal': latest_features_row['MACD_Signal'],
    'MACD_Diff': latest_features_row['MACD_Diff'],
    'BB_Upper': latest_features_row['BB_Upper'],
    'BB_Lower': latest_features_row['BB_Lower'],
    'BB_Width': latest_features_row['BB_Width'],
    'SMA_10': latest_features_row['SMA_10'],
    'SMA_20': latest_features_row['SMA_20'],
    'Volatility_10': latest_features_row['Volatility_10']
}])

# Append if file exists, else create
if os.path.exists(output_file):
    output_df.to_csv(output_file, mode='a', index=False, header=False)
else:
    output_df.to_csv(output_file, index=False)

print(f"\n✅ Prediction saved to {output_file}")
print(output_df)
