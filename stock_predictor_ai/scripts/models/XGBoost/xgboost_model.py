import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

def predict_xgb(stock_symbol, n_days=7):
    # ==== Paths ====
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.csv')

    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found!")
        return None

    # ==== Load Data ====
    data = pd.read_csv(file_path)
    if 'Date' not in data.columns:
        print("❌ Error: 'Date' column not found in CSV!")
        return None

    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)

    # ==== Detect Close column ====
    close_cols = [c for c in data.columns if 'Close' in c]
    if not close_cols:
        print("❌ Error: No 'Close' column found!")
        return None
    close_col = close_cols[0]

    df = data[[close_col]].copy()

    # ==== Feature Engineering ====
    df['SMA'] = df[close_col].rolling(14).mean()
    df['EMA'] = df[close_col].ewm(span=14, adjust=False).mean()
    df['Volatility'] = df[close_col].rolling(14).std()

    delta = df[close_col].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    RS = roll_up / roll_down
    df['RSI'] = 100 - (100 / (1 + RS))

    ema12 = df[close_col].ewm(span=12, adjust=False).mean()
    ema26 = df[close_col].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26

    df['BB_upper'] = df['SMA'] + 2 * df['Volatility']
    df['BB_lower'] = df['SMA'] - 2 * df['Volatility']

    df.dropna(inplace=True)

    # ==== Features & Target ====
    X = df.drop(columns=[close_col])
    y = df[close_col]

    if len(df) <= n_days:
        print(f"❌ Not enough data to predict {n_days} days!")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=n_days, shuffle=False)

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ==== Train Model ====
    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)

    # ==== Return predictions as DataFrame ====
    dates = data['Date'].tail(n_days).reset_index(drop=True)
    result = pd.DataFrame({
        'Date': dates,
        'Predicted_Close': preds
    })

    return result


# 🔹 Testing manually (optional)
if __name__ == "__main__":
    stock = input("Enter stock symbol (e.g., ABT): ").upper()
    preds = predict_xgb(stock)
    if preds is not None:
        print("\n📈 Predicted prices:")
        print(preds)
