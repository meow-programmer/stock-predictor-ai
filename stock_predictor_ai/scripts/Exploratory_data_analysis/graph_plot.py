import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
from scipy.signal import find_peaks

def plot_stock_graph(stock_symbol):
    """
    Plots High, Low, SMA, EMA, and volatility for a given stock symbol.
    Returns the latest SMA, EMA, and volatility values + Matplotlib figure.
    """

    # Base paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned')
    file_path = os.path.join(cleaned_path, f'{stock_symbol}.csv')

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    # Load data
    df = pd.read_csv(file_path, parse_dates=['Date'])
    close_col = f'Close_{stock_symbol}'
    high_col = f'High_{stock_symbol}'
    low_col = f'Low_{stock_symbol}'

    # Calculate indicators
    df['SMA'] = df[close_col].rolling(window=50).mean()
    df['EMA'] = df[close_col].ewm(span=20, adjust=False).mean()
    df['Volatility'] = df[close_col].rolling(window=20).std()

    # Find peaks and dips
    peaks, _ = find_peaks(df[close_col], distance=5)
    dips, _ = find_peaks(-df[close_col], distance=5)

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Date'], df[high_col], label='High', color='blue')
    ax.plot(df['Date'], df[low_col], label='Low', color='orange')
    ax.plot(df['Date'], df['SMA'], label='SMA (50)', color='purple')
    ax.plot(df['Date'], df['EMA'], label='EMA (20)', color='brown')
    ax.scatter(df['Date'][peaks], df[close_col][peaks], color='green', marker='^', label='Peaks')
    ax.scatter(df['Date'][dips], df[close_col][dips], color='red', marker='v', label='Dips')

    # Format date axis
    if len(df) > 365 * 2:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(1, 7)))
    elif len(df) > 90:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.gcf().autofmt_xdate()
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f'{stock_symbol} Price Analysis')
    ax.legend()
    plt.tight_layout()

    # Return indicators + figure
    result = {
        "stock": stock_symbol,
        "latest_SMA": round(df["SMA"].iloc[-1], 2),
        "latest_EMA": round(df["EMA"].iloc[-1], 2),
        "latest_volatility": round(df["Volatility"].iloc[-1], 2),
        "figure": fig
    }

    return result
