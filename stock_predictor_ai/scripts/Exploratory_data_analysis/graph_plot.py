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
print("3. View volatility table and volatility graph for specific stock")
choice = input("Enter 1, 2 or 3: ").strip()

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

if choice == '2':
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

elif choice == '3':
    print("What does volatility mean?")
    print("It is the measure of how stable your stock is over time. A stock that moves up and down rapidly is highly volatile, while one that moves steadily is less volatile.")
    
    stock = input("Enter which stock you want to see volatility table:").upper()
    file_path = os.path.join(cleaned_path, f'{stock}.xlsx')
    df = pd.read_excel(file_path)

    # Calculate volatility
    df['Volatility'] = df['Close_' + stock].rolling(window=20).std()

    # Create summary statistics DataFrame
    volatility_stats_df = pd.DataFrame({
        'Statistic': ['Mean Volatility', 'Max Volatility', 'Min Volatility', 'Latest Volatility'],
        'Value': [
            df['Volatility'].mean(),
            df['Volatility'].max(),
            df['Volatility'].min(),
            df['Volatility'].iloc[-1]
        ]
    }).round(2)

    # === Interactive Mode: Allow both plots to show at once ===
    plt.ion()  # Enable interactive mode

    # ----- Window 1: Volatility Graph -----
    fig1 = plt.figure(figsize=(12, 5))
    plt.plot(df['Date'], df['Volatility'], label='Volatility (20-day STD)', color='darkred')
    plt.xlabel("Date")
    plt.ylabel("Volatility")
    plt.title(f"{stock} Volatility Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    fig1.canvas.manager.set_window_title(f"{stock} Volatility Graph")
    fig1.show()

    # ----- Window 2: Volatility Table -----
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    ax2.axis('off')
    table = pd.plotting.table(ax2, volatility_stats_df, loc='center', colWidths=[0.5, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax2.set_title(f"{stock} Volatility Summary", fontsize=12, pad=20)
    plt.tight_layout()
    fig2.canvas.manager.set_window_title(f"{stock} Volatility Table")
    fig2.show()

    input("Press Enter to exit...")




else:
    print("Invalid input.")



