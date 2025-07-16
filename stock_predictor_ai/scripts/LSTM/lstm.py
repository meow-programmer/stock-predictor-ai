from keras.models import sequential













# ==== Aggregation by Year ====
yearly_df = df.groupby('Year').agg({
    'SMA_50': 'mean',
    'EMA_20': 'mean',
    'Volatility': 'mean',
    f'Close_{stock_symbol}': 'last'
}).reset_index()








