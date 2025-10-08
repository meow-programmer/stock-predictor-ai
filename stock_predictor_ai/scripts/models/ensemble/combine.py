# combine.py
import os
import pandas as pd
from scripts.models.LSTM.lstm import predict_lstm
from scripts.models.regression.linear_regression import predict_linear_regression
from scripts.models.regression.multiple_regression import predict_multiple_regression
from scripts.models.XGBoost.xgboost_model import predict_xgb

# Correct path: root/data/cleaned (not scripts/data/cleaned)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CLEANED_FOLDER = os.path.join(ROOT_DIR, 'data', 'cleaned')

def combine_predictions(stock_symbol):
    csv_path = os.path.join(CLEANED_FOLDER, f"{stock_symbol}.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found: {csv_path}")

    predictions = {
        "LSTM": predict_lstm(stock_symbol),
        "Linear Regression": predict_linear_regression(csv_path),
        "Multiple Regression": predict_multiple_regression(stock_symbol),
        "XGBoost": predict_xgb(stock_symbol)
    }

    summary = []
    combined_next_7_days = pd.DataFrame()

    for model_name, result in predictions.items():
        if "error" in result:
            summary.append({
                "Model": model_name,
                "Prediction": "Error",
                "MAE": "-",
                "RMSE": "-"
            })
        else:
            summary.append({
                "Model": model_name,
                "Prediction": round(result["prediction"], 2),
                "MAE": result.get("mae", "-"),
                "RMSE": result.get("rmse", "-")
            })
            if "next_7_days" in result:
                df_next7 = pd.DataFrame(result["next_7_days"], columns=[model_name])
                combined_next_7_days = pd.concat([combined_next_7_days, df_next7], axis=1)

    return {
        "summary_table": pd.DataFrame(summary),
        "combined_next_7_days": combined_next_7_days
    }
