import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Load file
stock_symbol = input("Enter stock   ymbol (e.g., AAPL): ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')
df = pd.read_excel(file_path)

# Convert to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate SMA
df['SMA_50'] = df['Close_' + stock_symbol].rolling(window=50).mean()

# Add Year column
df['Year'] = df['Date'].dt.year

# Drop NaN from SMA (initial 50 rows)
df = df.dropna(subset=['SMA_50'])

# Group by year
annual_sma = df.groupby('Year')['SMA_50'].mean().reset_index(name='Avg_SMA')
annual_close = df.groupby('Year')['Close_' + stock_symbol].last().reset_index(name='Year_End_Close')

# Merge both
yearly_df = pd.merge(annual_sma, annual_close, on='Year')

# Linear regression
x = yearly_df[['Avg_SMA']]
y = yearly_df['Year_End_Close']
model = LinearRegression()
model.fit(x, y)

# Predictions
yearly_df['Predicted_Close'] = model.predict(x)

def mae(model, x, y):
    model.fit(x, y)
    y_test = y
    y_pred = model.predict(x)

    # Mean Absolute Error
    mae_value = mean_absolute_error(y_test, y_pred)
    print("MAE:", mae_value)

    return mae_value  # optional, if you want to use it later

def mse(model,x,y):
    model.fit(x,y)
    y_test = y
    y_pred = model.predict(x)
    
    # Mean square error
    mse_value = mean_squared_error(y_test, y_pred)
    print("MSE: ",mse_value)

def rmse(model, x, y):
    model.fit(x, y)
    y_test = y
    y_pred = model.predict(x)

    # Root Mean Squared Error
    rmse_value = np.sqrt(mean_squared_error(y_test, y_pred))
    print("RMSE:", rmse_value)

def adjusted_r2(model, x, y):
    model.fit(x, y)
    r2 = model.score(x, y)
    n = x.shape[0]
    k = x.shape[1]
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    print("Adjusted R²:", adj_r2)

y_pred = model.predict(x)
def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true-y_pred
    is_small_error = np.abs(error) <= delta
    squared_loss = 0.5 * error ** 2
    linear_loss = delta * (np.abs(error) - 0.5 * delta)
    return np.mean(np.where(is_small_error, squared_loss, linear_loss))

# Evaluations
mae(model, x, y)
mse(model, x, y)
rmse(model, x ,y)
adjusted_r2(model, x, y)
print("Huber Loss:", huber_loss(y, y_pred))

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(yearly_df['Year'], yearly_df['Year_End_Close'], label='Actual Close', marker='o')
plt.plot(yearly_df['Year'], yearly_df['Predicted_Close'], label='Predicted Close', marker='x')
plt.xlabel('Year')
plt.ylabel('Closing Price')
plt.title(f"{stock_symbol} Year-End Price Prediction (Linear Regression)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()