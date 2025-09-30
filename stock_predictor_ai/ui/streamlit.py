import streamlit as st
import os
import pandas as pd
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_FOLDER = os.path.join(BASE_DIR, 'data', 'cleaned')

st.title("AI Quant Stock Dashboard")

# ----------------------
# Fetch new markers
# ----------------------
st.sidebar.subheader("Fetch / Update / Delete Stocks")
num_to_download = st.sidebar.number_input("Number of random stocks to download", min_value=1, max_value=100, value=10)
if st.sidebar.button("Fetch Stocks"):
    st.info("Fetching stocks...")
    subprocess.run(["python", os.path.join(BASE_DIR, "scripts", "fetch_data.py"), str(num_to_download)])
    st.success("Fetch complete. Reloading...")
    
# ----------------------
# Delete markers
# ----------------------
existing_stocks = [f.split('.')[0] for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx')]
stocks_to_delete = st.sidebar.multiselect("Select stocks to delete", existing_stocks)
if st.sidebar.button("Delete Selected Stocks"):
    st.warning("Deleting selected stocks...")
    for stock in stocks_to_delete:
        subprocess.run(["python", os.path.join(BASE_DIR, "scripts", "delete_data.py"), stock])
    st.success("Deletion complete. Reloading...")

# ----------------------
# Update stock prices
# ----------------------
if st.sidebar.button("Update Stocks"):
    st.info("Updating stock prices...")
    subprocess.run(["python", os.path.join(BASE_DIR, "scripts", "stock_update.py")])
    st.success("Stocks updated.")

# ----------------------
# Display all stocks
# ----------------------
st.subheader("Available Stocks")
existing_stocks = [f.split('.')[0] for f in os.listdir(CLEAN_FOLDER) if f.endswith('.xlsx')]
selected_stock = st.selectbox("Select a stock to view graph & predictions", existing_stocks)

# ----------------------
# Plot historical graph
# ----------------------
if selected_stock:
    df_stock = pd.read_excel(os.path.join(CLEAN_FOLDER, f"{selected_stock}.xlsx"), parse_dates=['Date'])
    st.line_chart(df_stock.set_index('Date')['Close'])

# ----------------------
# Combined predictions
# ----------------------
if st.button("Run Combined Predictions"):
    st.info(f"Running LSTM, Linear, Multiple Regression, XGBoost for {selected_stock}...")
    # Example: run each model and combine results
    # Assuming each script outputs a CSV with 'Date' and 'Prediction'
    lstm_pred = pd.read_csv(os.path.join(BASE_DIR, "predictions", f"{selected_stock}_lstm.csv"), parse_dates=['Date'])
    linear_pred = pd.read_csv(os.path.join(BASE_DIR, "predictions", f"{selected_stock}_linear.csv"), parse_dates=['Date'])
    multi_pred = pd.read_csv(os.path.join(BASE_DIR, "predictions", f"{selected_stock}_multi.csv"), parse_dates=['Date'])
    xgb_pred = pd.read_csv(os.path.join(BASE_DIR, "predictions", f"{selected_stock}_xgb.csv"), parse_dates=['Date'])

    combined = pd.DataFrame({
        'Date': lstm_pred['Date'],
        'LSTM': lstm_pred['Prediction'],
        'Linear': linear_pred['Prediction'],
        'Multiple': multi_pred['Prediction'],
        'XGBoost': xgb_pred['Prediction']
    })
    combined['Combined'] = combined[['LSTM', 'Linear', 'Multiple', 'XGBoost']].mean(axis=1)
    st.line_chart(combined.set_index('Date')[['LSTM', 'Linear', 'Multiple', 'XGBoost', 'Combined']])
    st.success("Predictions completed.")
