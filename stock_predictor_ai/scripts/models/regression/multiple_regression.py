from models.linear_regression import predict_linear
from models.multiple_regression import predict_multiple_regression
from models.xgb import predict_xgb
from models.lstm import predict_lstm

stock = "AAPL"  # example
results = []

# Linear Regression
lr = predict_linear(stock)
results.append(["Linear Regression", lr["prediction"], lr["mae"], lr["rmse"]])

# Multiple Regression
multi = predict_multiple_regression(stock)
if "error" not in multi:
    results.append(["Multiple Regression", multi["prediction"], multi["mae"], multi["rmse"]])
else:
    results.append(["Multiple Regression", "N/A", "—", "—"])

# XGBoost
xgb = predict_xgb(stock)
if xgb is not None:
    results.append(["XGBoost", xgb["prediction"], xgb["mae"], xgb["rmse"]])
else:
    results.append(["XGBoost", "N/A", "—", "—"])

# LSTM
lstm = predict_lstm(stock)
results.append(["LSTM", lstm["prediction"], lstm["mae"], lstm["rmse"]])

# Convert to DataFrame
df_results = pd.DataFrame(results, columns=["#", "Model", "Predicted Close", "MAE", "RMSE"])
print(df_results)
