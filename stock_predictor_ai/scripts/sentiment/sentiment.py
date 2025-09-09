import pandas as pd
import os
import random
from datetime import datetime, timedelta

# ---------------------------
# CONFIGURATION
# ---------------------------

SP500_FILE = 'data/raw/sp500_list.xlsx'
SENTIMENT_FILE = 'data/company_sentiment_ready.xlsx'
NEWS_DAYS = 365  # Fetch news for the last 1 year

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def generate_placeholder_sentiment():
    """Generate a placeholder sentiment score for testing purposes."""
    return random.choice([-1, 0, 1])  # Negative, Neutral, Positive

def fetch_news_for_stock(ticker):
    """
    Placeholder function to simulate fetching news.
    Replace this with real API call for actual news data.
    Returns a list of (date, headline, sentiment) tuples.
    """
    today = datetime.today()
    news_data = []
    for i in range(NEWS_DAYS):
        date = (today - timedelta(days=i)).date()
        headline = f"Sample news for {ticker} on {date}"
        sentiment = generate_placeholder_sentiment()
        news_data.append((date, ticker, sentiment, headline))
    return news_data

# ---------------------------
# MAIN SCRIPT
# ---------------------------

# Ensure directories exist
os.makedirs('data', exist_ok=True)

# Load S&P 500 tickers
if not os.path.exists(SP500_FILE):
    raise FileNotFoundError(f"{SP500_FILE} not found. Run fetch_data.py first!")

sp500 = pd.read_excel(SP500_FILE)
all_tickers = [ticker.replace('.', '-') for ticker in sp500['Symbol'].tolist()]

# Load or create sentiment file
if os.path.exists(SENTIMENT_FILE):
    sentiment_df = pd.read_excel(SENTIMENT_FILE)
else:
    sentiment_df = pd.DataFrame(columns=['Date', 'Stock', 'Sentiment', 'Headline'])

# Determine which tickers need news updates
existing_tickers = sentiment_df['Stock'].unique().tolist()
tickers_to_update = [t for t in all_tickers if t not in existing_tickers]

# Fetch news and sentiment for missing tickers
for ticker in tickers_to_update:
    print(f"[+] Fetching placeholder news for {ticker}...")
    news_entries = fetch_news_for_stock(ticker)
    ticker_df = pd.DataFrame(news_entries, columns=['Date', 'Stock', 'Sentiment', 'Headline'])
    sentiment_df = pd.concat([sentiment_df, ticker_df], ignore_index=True)

# Save the updated sentiment file
sentiment_df.to_excel(SENTIMENT_FILE, index=False)
print(f"[+] Sentiment file updated: {SENTIMENT_FILE}")
