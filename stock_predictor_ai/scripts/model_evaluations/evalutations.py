from sklearn.metrics import mean_absolute_error

def evaluate_model(model, x, y):
    model.fit(x, y)
    y_test = y
    y_pred = model.predict(x)

    # Mean Absolute Error
    mae_value = mean_absolute_error(y_test, y_pred)
    print("MAE:", mae_value)

    return mae_value  # optional, if you want to use it later
