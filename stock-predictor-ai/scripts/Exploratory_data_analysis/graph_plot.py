import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Ask the user for the stock symbol (e.g., 'ZBH')
stock_symbol = input("Enter stock symbol (e.g., ZBH): ").upper()

# Build file path based on input
file_path = f'data/cleaned/{stock_symbol}.xlsx'

# Read the Excel file
df = pd.read_excel(file_path)

# calculate moving averages (SMA and EMA)
df['SMA'] = df['Close_'+stock_symbol].rolling(window=50).mean()
df['EMA'] = df['Close_'+stock_symbol].ewm(span=20, adjust=False).mean()

# local dips and peaks
# Ask if user wants to display local dips and peaks
# plotting is also done below in user input format

show_extrema = input("Do you want to highlight local dips and peaks? (yes/no): ").lower().strip()

if show_extrema == "yes":
    print("\nLocal Peaks = short-term high points before price drops.")
    print("Local Dips  = short-term low points before price rises again.\n")

    close_col = 'Close_' + stock_symbol
    peaks, _ = find_peaks(df[close_col], distance=5)
    dips, _ = find_peaks(-df[close_col], distance=5)

    # plot local dips and peaks
    plt.scatter(df['Date'][peaks], df[close_col][peaks], color='green', marker='^', label='Peaks')
    plt.scatter(df['Date'][dips], df[close_col][dips], color='red', marker='v', label='Dips')



# Plot High and Low Prices
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['High_' + stock_symbol], label='High Price', color='blue')
plt.plot(df['Date'], df['Low_' + stock_symbol], label='Low Price', color='orange')

#Plot Moving Averages
plt.plot(df['Date'], df['SMA'], label='SMA', color='purple')
plt.plot(df['Date'], df['EMA'], label='EMA', color='brown')

# Titles and labels
plt.xlabel('Date')
plt.ylabel('Price')
plt.title(f"High and Low prices for {stock_symbol} over time")
plt.legend()

# Annotations
max_price = df['High_' + stock_symbol].max()
max_date = df['High_' + stock_symbol].idxmax()
plt.annotate(
    'Highest point',
    xy=(df['Date'][max_date], max_price),
    xytext=(df['Date'][max_date], max_price + 10),
    arrowprops=dict(facecolor='green', arrowstyle='->'),
    fontsize=8,
    color='green'
)

min_price = df['Low_' + stock_symbol].min()
min_date = df['Low_' + stock_symbol].idxmin()
plt.annotate(
    'Lowest point',
    xy=(df['Date'][min_date], min_price),
    xytext=(df['Date'][min_date], min_price - 10),
    arrowprops=dict(facecolor='red', arrowstyle='->'),
    fontsize=8,
    color='red'
)

plt.show()










