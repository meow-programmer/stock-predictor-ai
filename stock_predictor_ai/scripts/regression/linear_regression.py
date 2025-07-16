import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import os

# ==== Path Setup ====
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')
df = pd.read_excel(file_path)

# ==== Feature Engineering ====
df['Date'] = pd.to_datetime(df['Date'])
df['SMA_50'] = df[f'Close_{stock_symbol}'].rolling(window=50).mean()
df['Year'] = df['Date'].dt.year
df = df.dropna(subset=['SMA_50'])  # drop first 50 rows

# ==== Aggregate Yearly SMA and Close ====
annual_sma = df.groupby('Year')['SMA_50'].mean().reset_index(name='Avg_SMA')
annual_close = df.groupby('Year')[f'Close_{stock_symbol}'].last().reset_index(name='Year_End_Close')
yearly_df = pd.merge(annual_sma, annual_close, on='Year')

# ==== Model Training ====
x = yearly_df[['Avg_SMA']]
y = yearly_df['Year_End_Close']
model = LinearRegression()
model.fit(x, y)
y_pred = model.predict(x)
yearly_df['Predicted_Close'] = y_pred

# ==== Future Prediction ====
latest_sma = yearly_df['Avg_SMA'].iloc[-1]
next_year = yearly_df['Year'].max() + 1
future_pred = model.predict(np.array([[latest_sma]]))[0]

# Append future row
future_row = pd.DataFrame([{
    'Year': next_year,
    'Avg_SMA': np.nan,
    'Year_End_Close': np.nan,
    'Predicted_Close': future_pred
}])
yearly_df = pd.concat([yearly_df, future_row], ignore_index=True)

# ==== Evaluation Metrics ====
def mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def mse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)

def rmse(y_true, y_pred):
    return np.sqrt(mse(y_true, y_pred))

def adjusted_r2(y_true, y_pred, x):
    r2 = model.score(x, y_true)
    n, k = x.shape
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)

def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true - y_pred
    is_small = np.abs(error) <= delta
    squared = 0.5 * error ** 2
    linear = delta * (np.abs(error) - 0.5 * delta)
    return np.mean(np.where(is_small, squared, linear))

# ==== Print Metrics ====
print(f"\nMAE: {mae(y, y_pred):.2f}")
print(f"MSE: {mse(y, y_pred):.2f}")
print(f"RMSE: {rmse(y, y_pred):.2f}")
print(f"Adjusted R²: {adjusted_r2(y, y_pred, x):.4f}")
print(f"Huber Loss: {huber_loss(y, y_pred):.2f}")
print(f"\n📈 Predicted Close for Year {next_year}: {future_pred:.2f}")

# ==== Plotting ====
plt.figure(figsize=(10, 6))
plt.plot(yearly_df['Year'], yearly_df['Year_End_Close'], label='Actual Close', marker='o')
plt.plot(yearly_df['Year'], yearly_df['Predicted_Close'], label='Predicted Close', marker='x', linestyle='--')
plt.axvline(x=next_year - 1, color='gray', linestyle=':', label='Forecast Start')
plt.xlabel('Year')
plt.ylabel('Closing Price')
plt.title(f"{stock_symbol} Year-End Price Prediction using Avg_SMA (Linear Regression)")
plt.legend()
plt.grid(True)
plt.xticks(yearly_df['Year'].dropna().astype(int), rotation=45)
plt.tight_layout()
plt.show()
