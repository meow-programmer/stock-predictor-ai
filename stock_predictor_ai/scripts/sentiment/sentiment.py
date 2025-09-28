import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

# -----------------------------
# Directories
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
SENTIMENT_FOLDER = os.path.join(BASE_DIR, 'data', 'company_sentiment_ready')
os.makedirs(SENTIMENT_FOLDER, exist_ok=True)

# -----------------------------
# VADER sentiment analyzer
# -----------------------------
analyzer = SentimentIntensityAnalyzer()

# -----------------------------
# Get tickers
# -----------------------------
stock_files = [
    f for f in os.listdir(CLEANED_FOLDER)
    if f.endswith('.xlsx') and f != 'sp500_list.xlsx'
]
tickers = [os.path.splitext(f)[0].upper() for f in stock_files]

# -----------------------------
# Helper: fetch Yahoo Finance news for a ticker
# -----------------------------
def get_yahoo_news(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('li', {'class': 'js-stream-content'})
        news = []
        for item in items:
            title_tag = item.find('h3')
            if title_tag:
                title = title_tag.text.strip()
                # Get date if available
                time_tag = item.find('time')
                if time_tag and time_tag.has_attr('data-time'):
                    ts = int(time_tag['data-time'])
                    news_date = datetime.fromtimestamp(ts).date()
                else:
                    news_date = datetime.today().date()
                news.append({'Date': news_date, 'Headline': title})
        return news
    except Exception as e:
        print(f"[!] Failed to fetch news for {ticker}: {e}")
        return []

# -----------------------------
# Main loop
# -----------------------------
for ticker in tickers:
    sentiment_file = os.path.join(SENTIMENT_FOLDER, f'{ticker}_sentiment.xlsx')
    
    # Load existing sentiment file or create new
    if os.path.exists(sentiment_file):
        df_sent = pd.read_excel(sentiment_file, parse_dates=['Date'])
    else:
        df_sent = pd.DataFrame(columns=['Date', 'Sentiment', 'Last7Close'])

    # Determine date range for last 7 days
    today = datetime.today().date()
    start_date = today - timedelta(days=7)

    # Fetch news
    news_items = get_yahoo_news(ticker)
    news_items = [n for n in news_items if n['Date'] >= start_date]

    if not news_items:
        print(f"[=] No new news for {ticker} in last 7 days.")
        continue

    # Compute sentiment
    df_news = pd.DataFrame(news_items)
    df_news['Sentiment'] = df_news['Headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

    # Aggregate sentiment per day
    daily_sentiment = df_news.groupby('Date')['Sentiment'].mean().reset_index()

    # Fetch last 7 closing prices
    try:
        df_stock = yf.download(ticker, period='8d')  # extra day for safety
        df_stock = df_stock['Close'].tail(7).reset_index()
        last7close = df_stock['Close'].tolist()
        if len(last7close) < 7:
            last7close += [None] * (7 - len(last7close))
    except Exception:
        last7close = [None] * 7

    # Add closing prices column
    daily_sentiment['Last7Close'] = [last7close] * len(daily_sentiment)

    # Merge with existing sentiment file
    df_sent = pd.concat([df_sent, daily_sentiment], ignore_index=True)
    df_sent = df_sent.sort_values('Date').drop_duplicates('Date', keep='last').reset_index(drop=True)

    # Save updated Excel
    df_sent.to_excel(sentiment_file, index=False)
    print(f"[+] Updated {ticker}_sentiment.xlsx with {len(daily_sentiment)} new rows.")
