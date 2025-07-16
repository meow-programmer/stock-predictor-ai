import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import os

# ==== Path Setup ====
base_dir = os.path.abspath(os.path.join(os.getcwd(), 'stock_predictor_ai'))
file_path = os.path.join(base_dir, 'data', 'cleaned')
stock_symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
stock_file = os.path.join(file_path, f'{stock_symbol}.xlsx')
df = pd.read_excel(stock_file)

# ==== Feature Engineering ====
df['Date'] = pd.to_datetime(df['Date'])
df['SMA_50'] = df[f'Close_{stock_symbol}'].rolling(window=50).mean()
df['EMA_20'] = df[f'Close_{stock_symbol}'].ewm(span=20, adjust=False).mean()
df['Volatility'] = df[f'Close_{stock_symbol}'].rolling(window=20).std()
df['Year'] = df['Date'].dt.year
df.dropna(subset=['SMA_50', 'EMA_20', 'Volatility'], inplace=True)

# ==== Aggregation by Year ====
yearly_df = df.groupby('Year').agg({
    'SMA_50': 'mean',
    'EMA_20': 'mean',
    'Volatility': 'mean',
    f'Close_{stock_symbol}': 'last'
}).reset_index()

yearly_df.rename(columns={
    'SMA_50': 'Avg_SMA',
    'EMA_20': 'Avg_EMA',
    'Volatility': 'Avg_Volatility',
    f'Close_{stock_symbol}': 'Year_End_Close'
}, inplace=True)

# ==== Regression ====
x = yearly_df[['Avg_SMA', 'Avg_EMA', 'Avg_Volatility']]
y = yearly_df['Year_End_Close']
model = LinearRegression()
model.fit(x, y)
y_pred = model.predict(x)
yearly_df['Predicted_Close'] = y_pred

# ==== Future Prediction ====
latest_features = yearly_df[['Avg_SMA', 'Avg_EMA', 'Avg_Volatility']].iloc[-1].values.reshape(1, -1)
future_pred = model.predict(latest_features)[0]
next_year = yearly_df['Year'].max() + 1

# Append predicted future row
yearly_df = pd.concat([yearly_df, pd.DataFrame([{
    'Year': next_year,
    'Avg_SMA': np.nan,
    'Avg_EMA': np.nan,
    'Avg_Volatility': np.nan,
    'Year_End_Close': np.nan,
    'Predicted_Close': future_pred
}])], ignore_index=True)

# ==== Metrics ====
def mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def mse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)

def rmse(y_true, y_pred):
    return np.sqrt(mse(y_true, y_pred))

def adjusted_r2(y_true, y_pred, x):
    r2 = model.score(x, y_true)
    n = x.shape[0]
    k = x.shape[1]
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)

def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true - y_pred
    condition = np.abs(error) <= delta
    squared = 0.5 * error ** 2
    linear = delta * (np.abs(error) - 0.5 * delta)
    return np.mean(np.where(condition, squared, linear))

# ==== Display Metrics ====
print(f"\nMAE: {mae(y, y_pred)}")
print(f"MSE: {mse(y, y_pred)}")
print(f"RMSE: {rmse(y, y_pred)}")
print(f"Adjusted R²: {adjusted_r2(y, y_pred, x)}")
print(f"Huber Loss: {huber_loss(y, y_pred)}")
print(f"\n📈 Predicted Close for Year {next_year}: {future_pred:.2f}")

# ==== Plot ====
plt.figure(figsize=(10, 6))
plt.plot(yearly_df['Year'], yearly_df['Year_End_Close'], label='Actual Close', marker='o')
plt.plot(yearly_df['Year'], yearly_df['Predicted_Close'], label='Predicted Close', marker='x', linestyle='--')
plt.xlabel('Year')
plt.ylabel('Closing Price')
plt.title(f"{stock_symbol} Year-End Price Prediction (+Future) (Multi Linear Regression)")
plt.legend()
plt.grid(True)
plt.xticks(yearly_df['Year'][::2].dropna().astype(int))  # every 2nd year
plt.tight_layout()
plt.show()
