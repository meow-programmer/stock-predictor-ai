import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from model_evaluations.evaluations import evaluate_model #type: ignore
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

# Evaluations
evaluate_model(model, x, y)

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
