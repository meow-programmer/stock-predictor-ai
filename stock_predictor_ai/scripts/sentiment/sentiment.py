import os
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# --------------------------
# Setup
# --------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CLEANED_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')
SENTIMENT_FOLDER = os.path.join(BASE_DIR, 'data', 'company_sentiment_ready')
os.makedirs(SENTIMENT_FOLDER, exist_ok=True)

# Trading days
us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
today = pd.to_datetime(datetime.today().date())

# Sentiment analyzer
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# --------------------------
# Helper: average sentiment for a given day
# --------------------------
def get_sentiment_for_day(ticker, date):
    try:
        news = yf.Ticker(ticker).news
        if not news:
            return 0.0
        daily_scores = []
        for n in news:
            ts = pd.to_datetime(n.get("providerPublishTime", None), unit="s", errors="coerce")
            if ts is not None and ts.date() == date.date():
                title = n.get("title", "")
                if title:
                    daily_scores.append(sia.polarity_scores(title)["compound"])
        if daily_scores:
            return sum(daily_scores) / len(daily_scores)
        return 0.0
    except:
        return 0.0

# --------------------------
# Update last 30 days sentiment
# --------------------------
stock_files = [
    f for f in os.listdir(CLEANED_FOLDER)
    if f.endswith('.xlsx') and f != 'sp500_list.xlsx'
]

for file_name in stock_files:
    company = os.path.splitext(file_name)[0]
    sentiment_file = os.path.join(SENTIMENT_FOLDER, f'{company}_sentiment.xlsx')

    # Determine last 30 trading days
    last_30_days = pd.date_range(end=today, periods=30, freq=us_bd)

    # Load existing sentiment
    if os.path.exists(sentiment_file):
        df_sentiment = pd.read_excel(sentiment_file, parse_dates=['Date'])
    else:
        df_sentiment = pd.DataFrame(columns=['Date', 'Sentiment'])

    # Update sentiment for each of the last 30 days
    for d in last_30_days:
        if d not in df_sentiment['Date'].values:
            score = get_sentiment_for_day(company, d)
            df_sentiment = pd.concat([df_sentiment, pd.DataFrame({'Date':[d], 'Sentiment':[score]})], ignore_index=True)

    df_sentiment = df_sentiment.sort_values('Date').reset_index(drop=True)
    df_sentiment.to_excel(sentiment_file, index=False)
    print(f"[+] Updated {company} sentiment for last 30 trading days.")
