import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
RAW_FOLDER = os.path.join(DATA_FOLDER, 'raw')
CLEANED_FOLDER = os.path.join(DATA_FOLDER, 'cleaned')

os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# --- Imports for data management ---
from scripts.utils import data_manager as dm

# --- Imports for prediction ---
from scripts.models.LSTM.lstm import predict_lstm
from scripts.models.regression.linear_regression import predict_linear_regression
from scripts.models.regression.multiple_regression import predict_multiple_regression
from scripts.models.XGBoost.xgboost_model import predict_xgb
from scripts.models.ensemble.combine import combine_predictions  
from scripts.Exploratory_data_analysis import graph_plot

# ---------------------------
# --- Sidebar: Data Management ---
# ---------------------------
st.sidebar.header("📊 Data Management")

# --- Function to update live stock counts ---
def update_stock_counts():
    counts = dm.count_stocks()
    st.sidebar.markdown(f"**Stocks in raw folder:** {counts['raw_stocks']}")
    st.sidebar.markdown(f"**Stocks in cleaned folder:** {counts['cleaned_stocks']}")
    # Optionally show first 5 tickers as preview
    raw_tickers = counts["raw_tickers"]
    cleaned_tickers = counts["cleaned_tickers"]
    if raw_tickers:
        st.sidebar.markdown(f"Raw tickers: {', '.join(raw_tickers[:5])}{'...' if len(raw_tickers) > 5 else ''}")
    if cleaned_tickers:
        st.sidebar.markdown(f"Cleaned tickers: {', '.join(cleaned_tickers[:5])}{'...' if len(cleaned_tickers) > 5 else ''}")

# Initial stock count display
update_stock_counts()

# --- Download Stocks ---
st.sidebar.subheader("Download Stocks")
download_choice = st.sidebar.selectbox("Download type", ["Random 100", "Single", "Custom", "Random Range"])

if download_choice == "Single":
    single_ticker = st.sidebar.text_input("Enter ticker (e.g., AAPL)").upper()
elif download_choice == "Custom":
    custom_num = st.sidebar.number_input("Number of random stocks", min_value=1, max_value=500, value=10)
elif download_choice == "Random Range":
    min_range = st.sidebar.number_input("Min stocks", min_value=1, max_value=500, value=5)
    max_range = st.sidebar.number_input("Max stocks", min_value=1, max_value=500, value=20)

if st.sidebar.button("Download"):
    with st.spinner("Downloading and cleaning..."):
        if download_choice == "Random 100":
            result = dm.fetch_stocks(choice="random_100", logger=st.write)
        elif download_choice == "Single":
            result = dm.fetch_stocks(choice="single", ticker=single_ticker, logger=st.write)
        elif download_choice == "Custom":
            result = dm.fetch_stocks(choice="custom", num=custom_num, logger=st.write)
        elif download_choice == "Random Range":
            result = dm.fetch_stocks(choice="range", min_num=min_range, max_num=max_range, logger=st.write)
        st.success(result["message"])
    update_stock_counts()  # <-- refresh counts after download

st.sidebar.markdown("---")

# --- Update Stocks ---
if st.sidebar.button("Update All Stocks"):
    with st.spinner("Updating all stocks..."):
        result = dm.update_stocks(logger=st.write)
        st.success(result["message"])
    update_stock_counts()  # <-- refresh counts after update

st.sidebar.markdown("---")

# --- Delete Stocks ---
st.sidebar.subheader("Delete Stocks")
delete_mode = st.sidebar.radio("Delete by", ["Random Count", "Specific Tickers"])

if delete_mode == "Random Count":
    delete_count = st.sidebar.number_input("How many random stocks to delete?", min_value=1, max_value=500, value=5)
    if st.sidebar.button("Delete Random"):
        result = dm.delete_stocks(random_count=delete_count, logger=st.write)
        st.success(result["message"])
        update_stock_counts()  # <-- refresh counts after delete
elif delete_mode == "Specific Tickers":
    tickers_input = st.sidebar.text_input("Enter tickers comma-separated").upper()
    tickers_to_delete = [t.strip() for t in tickers_input.split(",") if t.strip()]
    if st.sidebar.button("Delete Specific"):
        result = dm.delete_stocks(tickers=tickers_to_delete, logger=st.write)
        st.success(result["message"])
        update_stock_counts()  # <-- refresh counts after delete

# ---------------------------
# --- Main: Stock Prediction & Graph ---
# ---------------------------
st.header("📈 Stock Prediction & Analysis")

# List available cleaned stocks
available_stocks = [f.replace(".csv", "") for f in os.listdir(CLEANED_FOLDER) if f.endswith(".csv")]

if not available_stocks:
    st.warning("No cleaned stock data found! Download & clean some stocks first.")
else:
    selected_stock = st.selectbox("Select a stock", available_stocks)

    # Plot stock graph
    if st.button("Show Stock Graph"):
        graph_result = graph_plot.plot_stock_graph(selected_stock)
        if graph_result:
            st.pyplot(graph_result["figure"])
            st.write(f"**Latest SMA:** {graph_result['latest_SMA']}")
            st.write(f"**Latest EMA:** {graph_result['latest_EMA']}")
            st.write(f"**Latest Volatility:** {graph_result['latest_volatility']}")
        else:
            st.error("Failed to load graph for this stock.")

    # --- Combined Prediction for All Models ---
    st.subheader("Combined Prediction")

    if st.button("Predict All Models"):
        with st.spinner("Running all models..."):
            combined_results = {}
            csv_path = os.path.join(CLEANED_FOLDER, f"{selected_stock}.csv")
            
            try:
                combined_results["LSTM"] = predict_lstm(selected_stock)
                combined_results["Linear Regression"] = predict_linear_regression(csv_path)
                combined_results["Multiple Regression"] = predict_multiple_regression(selected_stock)
                combined_results["XGBoost"] = predict_xgb(selected_stock)
                
                for model, result in combined_results.items():
                    st.markdown(f"**{model} Prediction:**")
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(f"Next week's predicted price: {result['prediction']}")
                        if "next_7_days" in result:
                            st.line_chart(result["next_7_days"])
                        if "mae" in result:
                            st.write(f"MAE: {result['mae']}, RMSE: {result['rmse']}")
                    st.write("---")
            except Exception as e:
                st.error(f"Failed to run predictions: {e}")

# --- Ensemble / Combined Output ---
st.subheader("Ensemble / Combined Output")

if st.button("Predict Ensemble (All Models)"):
    if not available_stocks:
        st.warning("No cleaned stock data found! Download & clean some stocks first.")
    else:
        with st.spinner("Running ensemble predictions..."):
            try:
                ensemble_result = combine_predictions(selected_stock)

                # Show summary table
                st.write("### Ensemble Summary Table")
                st.dataframe(ensemble_result["summary_table"])

                # Show combined next 7 days chart
                if "combined_next_7_days" in ensemble_result and not ensemble_result["combined_next_7_days"].empty:
                    st.write("### Next 7 Days Forecast Comparison")
                    st.line_chart(ensemble_result["combined_next_7_days"])

            except Exception as e:
                st.error(f"Ensemble prediction failed: {e}")
