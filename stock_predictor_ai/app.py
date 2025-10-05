import streamlit as st
import os
import pandas as pd

# === Import all model functions ===
from scripts.models.regression.linear_regression import predict_linear_regression
from scripts.models.regression.multiple_regression import predict_multiple_regression
from scripts.models.XGBoost.xgboost_model import predict_xgb
from scripts.models.LSTM.lstm import predict_lstm

# === Paths ===
base_dir = os.path.abspath(os.path.dirname(__file__))
cleaned_path = os.path.join(base_dir, "data", "cleaned")

# === UI Title ===
st.title("📈 Stock Prediction Dashboard")
st.write("Select a stock from the list below to see model predictions:")

# === Get all available CSV files ===
stocks = [f.replace(".csv", "") for f in os.listdir(cleaned_path) if f.endswith(".csv")]

if not stocks:
    st.warning("No stock files found in data/cleaned folder!")
else:
    selected_stock = st.selectbox("Choose a stock:", stocks)

    if st.button("Predict"):
        st.write(f"### Predictions for {selected_stock}")

        # Run models one by one
        try:
            lin_pred = predict_linear_regression(selected_stock)
            mult_pred = predict_multiple_regression(selected_stock)
            xgb_pred = predict_xgb(selected_stock)
            lstm_pred = predict_lstm(selected_stock)

            data = {
                "Model": ["Linear Regression", "Multiple Regression", "XGBoost", "LSTM"],
                "Predicted Price": [
                    lin_pred.get("prediction", "N/A"),
                    mult_pred.get("prediction", "N/A"),
                    xgb_pred.get("prediction", "N/A"),
                    lstm_pred.get("prediction", "N/A")
                ],
                "MAE": [
                    lin_pred.get("mae", "—"),
                    mult_pred.get("mae", "—"),
                    xgb_pred.get("mae", "—"),
                    lstm_pred.get("mae", "—")
                ],
                "RMSE": [
                    lin_pred.get("rmse", "—"),
                    mult_pred.get("rmse", "—"),
                    xgb_pred.get("rmse", "—"),
                    lstm_pred.get("rmse", "—")
                ],
            }

            st.dataframe(pd.DataFrame(data))

        except Exception as e:
            st.error(f"Error: {e}")
