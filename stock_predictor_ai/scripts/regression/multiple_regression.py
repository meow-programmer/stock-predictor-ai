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
df['SMA_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).mean()
df['SMA_20'] = df[f'Close_{stock_symbol}'].rolling(window=20).mean()
df['Volatility_10'] = df[f'Close_{stock_symbol}'].rolling(window=10).std()
df.dropna(inplace=True)

# ==== Feature and Target Engineering ====
# Predict the close price 5 business days ahead
df['Target_Close'] = df[f'Close_{stock_symbol}'].shift(-5)

features = ['SMA_10', 'SMA_20', 'Volatility_10']
df.dropna(inplace=True)

x = df[features]
y = df['Target_Close']

# ==== Train/Test Split ====
split_point = int(len(df) * 0.8)
x_train, x_test = x[:split_point], x[split_point:]
y_train, y_test = y[:split_point], y[split_point:]

# ==== Model Training ====
model = LinearRegression()
model.fit(x_train, y_train)

# ==== Evaluation ====
y_pred = model.predict(x_test)
print("\nEvaluation Metrics (Test Set)")
print("----------------------------")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

# ==== Next Week Prediction ====
latest_data = df[features].iloc[-1].values.reshape(1, -1)
next_week_pred = model.predict(latest_data)[0]
latest_date = df['Date'].max()
next_week_date = latest_date + timedelta(days=7)

print("\n📈 Predicted Closing Price")
print("----------------------------")
print(f"From: {latest_date.date()}  -->  To: {next_week_date.date()}  |  Predicted Close: ${next_week_pred:.2f}")