import pandas as pd
import numpy as np

def combine_models(stock_symbol, lstm_model, multi_reg_model, linear_model, xgb_model, input_data):
    """
    Combines predictions from LSTM, multiple linear regression, linear regression, and XGBoost models.
    
    Args:
        stock_symbol (str): Ticker symbol.
        lstm_model: Trained LSTM model.
        multi_reg_model: Trained multiple linear regression model.
        linear_model: Trained simple linear regression model.
        xgb_model: Trained XGBoost model.
        input_data (DataFrame or numpy array): Features for prediction.
        
    Returns:
        dict: Combined results for this stock.
    """

    results = {}

    # 1️⃣ LSTM prediction
    lstm_pred = lstm_model.predict(input_data)
    results['LSTM'] = lstm_pred.flatten() if hasattr(lstm_pred, 'flatten') else lstm_pred

    # 2️⃣ Multiple Linear Regression prediction
    multi_reg_pred = multi_reg_model.predict(input_data)
    results['MultiLinearRegression'] = multi_reg_pred.flatten() if hasattr(multi_reg_pred, 'flatten') else multi_reg_pred

    # 3️⃣ Simple Linear Regression prediction
    linear_pred = linear_model.predict(input_data)
    results['LinearRegression'] = linear_pred.flatten() if hasattr(linear_pred, 'flatten') else linear_pred

    # 4️⃣ XGBoost prediction
    xgb_pred = xgb_model.predict(input_data)
    results['XGBoost'] = xgb_pred.flatten() if hasattr(xgb_pred, 'flatten') else xgb_pred

    # 5️⃣ Combined prediction (simple average)
    results['Combined'] = np.mean(list(results.values()), axis=0)

    # Return as DataFrame for easier plotting/UI
    combined_df = pd.DataFrame(results)
    combined_df['Date'] = input_data.index if hasattr(input_data, 'index') else range(len(combined_df))
    return combined_df

# Example usage:
# df_combined = combine_models('AAPL', lstm_model, multi_reg_model, linear_model, xgb_model, X_input)
# print(df_combined.head())
