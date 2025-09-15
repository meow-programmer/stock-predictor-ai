import os
import pandas as pd
from datetime import datetime
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

# Today's date
today = pd.to_datetime(datetime.today().date())

# Define U.S. trading days (skip weekends + holidays)
us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())

# Sentiment analyzer
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# --------------------------
# Helper: get average sentiment from Yahoo headlines
# --------------------------
def get_sentiment_for_day(ticker, date):
    """
    Fetch Yahoo Finance headlines for `ticker` and return avg sentiment for `date`.
    """
    try:
        news = yf.Ticker(ticker).news
        if not news:
            return None

        # Filter news for given date
        daily_scores = []
        for n in news:
            ts = pd.to_datetime(n.get("providerPublishTime", None), unit="s", errors="coerce")
            if ts is not None and ts.date() == date.date():
                title = n.get("title", "")
                if title:
                    score = sia.polarity_scores(title)["compound"]
                    daily_scores.append(score)

        if daily_scores:
            return sum(daily_scores) / len(daily_scores)
        else:
            return None
    except Exception as e:
        print(f"[!] Error fetching news for {ticker}: {e}")
        return None

# --------------------------
# Main update loop
# --------------------------
stock_files = [
    f for f in os.listdir(CLEANED_FOLDER)
    if f.endswith(('.xlsx', '.csv')) and f != 'sp500_list.xlsx'
]

for file_name in stock_files:
    company = os.path.splitext(file_name)[0]
    sentiment_file = os.path.join(SENTIMENT_FOLDER, f'{company}_sentiment.xlsx')

    if os.path.exists(sentiment_file):
        df_sentiment = pd.read_excel(sentiment_file, parse_dates=['Date'])
        last_date = df_sentiment['Date'].max()

        # Only update forward
        if last_date < today:
            new_dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                      end=today, freq=us_bd)

            if not new_dates.empty:
                new_rows = []
                for d in new_dates:
                    sentiment = get_sentiment_for_day(company, d)
                    if sentiment is None:
                        sentiment = 0.0  # fallback
                    new_rows.append({"Date": d, "Sentiment": sentiment})

                df_sentiment = pd.concat([df_sentiment, pd.DataFrame(new_rows)], ignore_index=True)
                df_sentiment = df_sentiment.sort_values("Date").reset_index(drop=True)
                df_sentiment.to_excel(sentiment_file, index=False)

                print(f"[+] Updated {company} with {len(new_rows)} new sentiment rows.")
            else:
                print(f"[=] {company} already up-to-date.")
        else:
            print(f"[=] {company} already at {last_date.date()}.")
    else:
        print(f"[!] Sentiment file for {company} not found. Run placeholder creation first.")
