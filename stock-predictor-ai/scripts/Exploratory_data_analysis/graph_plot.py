import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

# Base directory setup
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
cleaned_path = os.path.join(base_dir, 'data', 'cleaned')

# Ask user what they want
print("Choose an option:")
print("1. View single stock")
print("2. Compare two stocks")
choice = input("Enter 1 or 2: ").strip()

if choice == '1':
    stock_symbol = input("Enter stock symbol (e.g., ZBH): ").upper()
    file_path = os.path.join(cleaned_path, f'{stock_symbol}.xlsx')
    df = pd.read_excel(file_path)

    # Moving averages
    df['SMA'] = df['Close_' + stock_symbol].rolling(window=50).mean()
    df['EMA'] = df['Close_' + stock_symbol].ewm(span=20, adjust=False).mean()

    # Ask if local peaks/dips are to be shown
    show_extrema = input("Show local dips and peaks? (yes/no): ").strip().lower()
    if show_extrema == "yes":
        print("\nLocal Peaks = short-term high points before price drops.")
        print("Local Dips  = short-term low points before price rises again.\n")
        close_col = 'Close_' + stock_symbol
        peaks, _ = find_peaks(df[close_col], distance=5)
        dips, _ = find_peaks(-df[close_col], distance=5)
        plt.scatter(df['Date'][peaks], df[close_col][peaks], color='green', marker='^', label='Peaks')
        plt.scatter(df['Date'][dips], df[close_col][dips], color='red', marker='v', label='Dips')

    # Plot high, low, SMA, EMA
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['High_' + stock_symbol], label='High Price', color='blue')
    plt.plot(df['Date'], df['Low_' + stock_symbol], label='Low Price', color='orange')
    plt.plot(df['Date'], df['SMA'], label='SMA', color='purple')
    plt.plot(df['Date'], df['EMA'], label='EMA', color='brown')

    # Annotations
    max_price = df['High_' + stock_symbol].max()
    max_date = df['High_' + stock_symbol].idxmax()
    plt.annotate('Highest point',
                 xy=(df['Date'][max_date], max_price),
                 xytext=(df['Date'][max_date], max_price + 10),
                 arrowprops=dict(facecolor='green', arrowstyle='->'),
                 fontsize=8, color='green')

    min_price = df['Low_' + stock_symbol].min()
    min_date = df['Low_' + stock_symbol].idxmin()
    plt.annotate('Lowest point',
                 xy=(df['Date'][min_date], min_price),
                 xytext=(df['Date'][min_date], min_price - 10),
                 arrowprops=dict(facecolor='red', arrowstyle='->'),
                 fontsize=8, color='red')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f"{stock_symbol} Price Analysis")
    plt.legend()
    plt.tight_layout()
    plt.show()

elif choice == '2':
    stock1 = input("Enter first stock symbol: ").upper()
    stock2 = input("Enter second stock symbol: ").upper()

    file1 = os.path.join(cleaned_path, f'{stock1}.xlsx')
    file2 = os.path.join(cleaned_path, f'{stock2}.xlsx')

    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    plt.figure(figsize=(12, 6))
    plt.plot(df1['Date'], df1['Close_' + stock1], label=f"{stock1} Close", color='blue')
    plt.plot(df2['Date'], df2['Close_' + stock2], label=f"{stock2} Close", color='green')

    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    plt.title(f"Comparison: {stock1} vs {stock2}")
    plt.legend()
    plt.tight_layout()
    plt.show()


else:
    print("Invalid input.")


