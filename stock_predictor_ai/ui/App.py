import streamlit as st
import os
import pandas as pd
import subprocess
from datetime import datetime

# -----------------------------
# Base directories
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
CLEAN_FOLDER = os.path.join(BASE_DIR, "data", "cleaned")
PREDICTIONS_FOLDER = os.path.join(BASE_DIR, "predictions")
os.makedirs(PREDICTIONS_FOLDER, exist_ok=True)

st.title("AI Quant Stock Dashboard")

# -----------------------------
# Sidebar: Fetch / Delete / Update
# -----------------------------
st.sidebar.header("Manage Stocks")

# 1️⃣ Fetch new stocks
num_to_download = st.sidebar.number_input("Number of random stocks to download", min_value=1, max_value=100, value=10)
if st.sidebar.button("Fetch Stocks"):
    st.info("Fetching stocks...")
    subprocess.run(["python", os.path.join(SCRIPTS_DIR, "fetch_data.py"), str(num_to_download)])
    st.success("Fetch complete. Reload the page to see new stocks.")

# 2️⃣ Delete stocks
existing_stocks = [f.split('.')[0] for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx')]
stocks_to_delete = st.sidebar.multiselect("Select stocks to delete", existing_stocks)
if st.sidebar.button("Delete Selected Stocks"):
    st.warning("Deleting selected stocks...")
    for stock in stocks_to_delete:
        subprocess.run(["python", os.path.join(SCRIPTS_DIR, "delete_data.py"), stock])
    st.success("Deletion complete. Reload the page.")

# 3️⃣ Update stock prices
if st.sidebar.button("Update Stocks"):
    st.info("Updating stock prices...")
    subprocess.run(["python", os.path.join(SCRIPTS_DIR, "stock_update.py")])
    st.success("Stocks updated.")

# -----------------------------
# Display all stocks
# -----------------------------
st.subheader("Available Stocks")
existing_stocks = [f.split('.')[0] for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx')]
selected_stock = st.selectbox("Select a stock to view graph & predictions", existing_stocks)

# -----------------------------
# Plot historical graph
# -----------------------------
if selected_stock:
    df_stock = pd.read_excel(os.path.join(CLEAN_FOLDER, f"{selected_stock}.xlsx"), parse_dates=['Date'])
    st.line_chart(df_stock.set_index('Date')['Close'])

# -----------------------------
# Combined Predictions
# -----------------------------
def run_prediction_script(script_name, stock):
    """Run a prediction script and save CSV for that stock"""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    subprocess.run(["python", script_path, stock, PREDICTIONS_FOLDER])

if st.button("Run Combined Predictions"):
    st.info(f"Running LSTM, Linear, Multiple Regression, XGBoost for {selected_stock}...")
    
    # Run each script and save results in predictions folder
    run_prediction_script("lstm.py", selected_stock)
    run_prediction_script("linear_regression.py", selected_stock)
    run_prediction_script("multiple_regression.py", selected_stock)
    run_prediction_script("xgboost_model.py", selected_stock)

    # Load predictions
    lstm_pred = pd.read_csv(os.path.join(PREDICTIONS_FOLDER, f"{selected_stock}_lstm.csv"), parse_dates=['Date'])
    linear_pred = pd.read_csv(os.path.join(PREDICTIONS_FOLDER, f"{selected_stock}_linear.csv"), parse_dates=['Date'])
    multi_pred = pd.read_csv(os.path.join(PREDICTIONS_FOLDER, f"{selected_stock}_multi.csv"), parse_dates=['Date'])
    xgb_pred = pd.read_csv(os.path.join(PREDICTIONS_FOLDER, f"{selected_stock}_xgb.csv"), parse_dates=['Date'])

    # Combine predictions
    combined = pd.DataFrame({
        'Date': lstm_pred['Date'],
        'LSTM': lstm_pred['Prediction'],
        'Linear': linear_pred['Prediction'],
        'Multiple': multi_pred['Prediction'],
        'XGBoost': xgb_pred['Prediction']
    })
    combined['Combined'] = combined[['LSTM', 'Linear', 'Multiple', 'XGBoost']].mean(axis=1)

    st.line_chart(combined.set_index('Date')[['LSTM', 'Linear', 'Multiple', 'XGBoost', 'Combined']])
    st.success("Combined predictions completed!")
