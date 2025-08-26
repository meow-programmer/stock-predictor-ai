import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ==== Path Setup ====
stock_symbol = input("Enter stock symbol: ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')

# Reading the data
df = pd.read_excel(file_path)

# Assuming you want to predict 'Close' price column
data = df[['Close']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# ==== Sequence Creation ====
sequence_length = 60  # Using past 60 days to predict the next day
x, y = [], []
for i in range(sequence_length, len(scaled_data)):
    x.append(scaled_data[i - sequence_length:i, 0])
    y.append(scaled_data[i, 0])

x = np.array(x)
y = np.array(y)

# Reshaping for LSTM input
x = np.reshape(x, (x.shape[0], x.shape[1], 1))

# ==== LSTM Model ====
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x.shape[1], 1)))
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))

model.add(Dense(units=25))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# ==== Model Training ====
model.fit(x, y, batch_size=32, epochs=25)

# ==== Prediction ====
test_data = scaled_data[-sequence_length:]
x_test = []
x_test.append(test_data)

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

predicted_price = model.predict(x_test)
predicted_price = scaler.inverse_transform(predicted_price)  # Back to original scale
print(predicted_price)
