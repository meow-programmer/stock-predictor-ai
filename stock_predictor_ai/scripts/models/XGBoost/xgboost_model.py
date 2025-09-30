import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

def predict_xgb(stock_symbol, n_days=7):
    # 1️⃣ File path (CSV)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.csv')
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found!")
        return None

    # 2️⃣ Read CSV
    data = pd.read_csv(file_path)

    # Ensure Date is datetime
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
        data.sort_values('Date', inplace=True)

    # Find closing price column
    close_col = [c for c in data.columns if c.startswith("Close") and stock_symbol in c]
    if not close_col:
        print(f"Error: Closing price column for {stock_symbol} not found!")
        return None
    close_col = close_col[0]

    df = data[[close_col]].copy()

    # 3️⃣ Add technical indicators
    df['SMA'] = df[close_col].rolling(14).mean()
    df['EMA'] = df[close_col].ewm(span=14, adjust=False).mean()
    df['Volatility'] = df[close_col].rolling(14).std()

    # RSI
    delta = df[close_col].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    RS = roll_up / roll_down
    df['RSI'] = 100 - (100 / (1 + RS))
        
    # MACD
    ema12 = df[close_col].ewm(span=12, adjust=False).mean()
    ema26 = df[close_col].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26

    # Bollinger Bands
    df['BB_upper'] = df['SMA'] + 2*df['Volatility']
    df['BB_lower'] = df['SMA'] - 2*df['Volatility']

    # Drop NaNs
    df.dropna(inplace=True)

    # 4️⃣ Prepare features and target
    X = df.drop(columns=[close_col])
    y = df[close_col]

    # 5️⃣ Train-test split (last n_days as test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=n_days, shuffle=False)

    # 6️⃣ Scale features (optional, XGBoost can handle unscaled data too)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 7️⃣ Train XGBoost
    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5)
    model.fit(X_train_scaled, y_train)

    # 8️⃣ Predict next n_days
    next_preds = model.predict(X_test_scaled)

    return next_preds

# 🔹 Example usage
if __name__ == "__main__":
    stock = input("Enter stock symbol (e.g., ABT): ").upper()
    preds = predict_xgb(stock)
    if preds is not None:
        print("\nXGBoost predicted prices for next days:")
        for i, price in enumerate(preds, 1):
            print(f"Day {i}: {price:.2f}")
