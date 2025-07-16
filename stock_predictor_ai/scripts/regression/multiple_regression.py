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

# ==== Regression (Training) ====
x = yearly_df[['Avg_SMA', 'Avg_EMA', 'Avg_Volatility']]
y = yearly_df['Year_End_Close']
model = LinearRegression()
model.fit(x, y)
y_pred = model.predict(x)
yearly_df['Predicted_Close'] = y_pred

# ==== Prediction Mode Input ====
mode = input("Prediction type (monthly / yearly / decadely): ").strip().lower()
if mode == 'monthly':
    steps = 12
    interval = 1/12
elif mode == 'yearly':
    steps = 10
    interval = 1
elif mode == 'decadely':
    steps = 100
    interval = 1
else:
    print("Invalid mode. Defaulting to yearly.")
    steps = 10
    interval = 1

# ==== Simulate Future Predictions ====
latest_year = yearly_df['Year'].max()
latest_features = yearly_df[['Avg_SMA', 'Avg_EMA', 'Avg_Volatility']].iloc[-1].values

# Optional: adjust decay rates per feature
decay_rates = np.array([0.995, 0.997, 0.990])  # tweak to experiment
simulated_features = latest_features.copy()

future_years = []
future_preds = []

for i in range(1, steps + 1):
    future_time = latest_year + (i * interval)
    pred = model.predict(simulated_features.reshape(1, -1))[0]
    
    future_years.append(future_time)
    future_preds.append(pred)

    # simulate decaying features slightly for each step
    simulated_features *= decay_rates

# ==== Append Predictions ====
future_df = pd.DataFrame({
    'Year': future_years,
    'Avg_SMA': [np.nan] * steps,
    'Avg_EMA': [np.nan] * steps,
    'Avg_Volatility': [np.nan] * steps,
    'Year_End_Close': [np.nan] * steps,
    'Predicted_Close': future_preds
})

yearly_df = pd.concat([yearly_df, future_df], ignore_index=True)

# ==== Metrics (only historical) ====
def mae(y_true, y_pred): return mean_absolute_error(y_true, y_pred)
def mse(y_true, y_pred): return mean_squared_error(y_true, y_pred)
def rmse(y_true, y_pred): return np.sqrt(mse(y_true, y_pred))
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
print(f"\n📈 Predicted Close for Final Year {future_years[-1]:.2f}: {future_preds[-1]:.2f}")

fig, axs = plt.subplots(2, 1, figsize=(12, 10))

# Historical
axs[0].plot(yearly_df['Year'][:len(y)], yearly_df['Year_End_Close'][:len(y)], label='Actual Close', marker='o')
axs[0].plot(yearly_df['Year'][:len(y)], yearly_df['Predicted_Close'][:len(y)], label='Predicted Close', marker='x')
axs[0].set_title("Historical Performance")
axs[0].legend()
axs[0].grid(True)

# Future
axs[1].plot(yearly_df['Year'][len(y):], yearly_df['Predicted_Close'][len(y):], label='Future Predictions', marker='x', linestyle='--', color='orange')
axs[1].set_title(f"Future Forecast ({mode.capitalize()})")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()

if mode == 'monthly':
    plot_df = yearly_df.copy()
    mask = plot_df['Year'] % (1/2) == 0  # or use modulo on index
    plot_df = plot_df[mask | (plot_df['Year'] <= latest_year)]


# ==== Plot ====
plt.figure(figsize=(12, 6))
plt.plot(yearly_df['Year'], yearly_df['Year_End_Close'], label='Actual Close', marker='o')
plt.plot(yearly_df['Year'], yearly_df['Predicted_Close'], label='Predicted Close', marker='x', linestyle='--')
plt.axvline(x=latest_year, color='gray', linestyle=':', label='Forecast Start')
plt.xlabel('Year')
plt.ylabel('Closing Price')
plt.title(f"{stock_symbol} Closing Price Forecast - {mode.capitalize()} Mode")
plt.legend()
plt.grid(True)
plt.xticks(np.round(yearly_df['Year'].dropna(), 2), rotation=45)
plt.xlim(yearly_df['Year'].min(), yearly_df['Year'].max() + 10)  # adjust based on mode
plt.tight_layout()
plt.show()
