import streamlit as st
import os
import pandas as pd

# === Import all model functions ===
from scripts.models.regression.linear_regression import predict_linear_regression
from scripts.models.regression.multiple_regression import predict_multiple_regression
from scripts.models.XGBoost.xgboost_model import predict_xgb
from scripts.models.LSTM.lstm import predict_lstm
from scripts.Exploratory_data_analysis.graph_plot import plot_stock_graph  # ✅ make sure function name matches

# === Paths ===
base_dir = os.path.abspath(os.path.dirname(__file__))
cleaned_path = os.path.join(base_dir, "data", "cleaned")

# === UI Title ===
st.title("📈 Stock Prediction Dashboard")
st.write("Select a stock from the list below to see model predictions and graph.")

# === Get all available CSV files ===
stocks = [f.replace(".csv", "") for f in os.listdir(cleaned_path) if f.endswith(".csv")]

if not stocks:
    st.warning("No stock files found in data/cleaned folder!")
else:
    selected_stock = st.selectbox("Choose a stock:", stocks)

    if st.button("Predict and Show Graph"):
        st.write(f"## 📊 Analysis for {selected_stock}")

        # --- 📈 Plot Graph ---
        try:
            graph_data = plot_stock_graph(selected_stock)
            if graph_data:
                st.pyplot(graph_data["figure"])
                st.write(f"**Latest SMA (50):** {graph_data['latest_SMA']}")
                st.write(f"**Latest EMA (20):** {graph_data['latest_EMA']}")
                st.write(f"**Latest Volatility:** {graph_data['latest_volatility']}")
            else:
                st.warning("No graph data found or error loading stock data.")
        except Exception as e:
            st.error(f"Graph error: {e}")

        # --- 🤖 Run Predictions ---
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

            st.subheader("📉 Model Predictions")
            st.dataframe(pd.DataFrame(data))

        except Exception as e:
            st.error(f"Model prediction error: {e}")
