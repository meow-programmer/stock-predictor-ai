# LSTM is sequence based
import numpy as pd
import os
from sklearn.preprocessing import MinMaxScaler
from keras.models import sequential

# ==== Path Setup ====
stock_symbol = input("Enter stock symbol: ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')
df = read.excel(file_path)

# ==== sequence creation ====
sequence_length = 60 # use past 60 day to predict next day
x, y = [], []
for i in range(sequence_length, len(scaled_data)):
  x.append(scaled_data[i - sequence_length: i, 0])
  y.append(scaled_data[i,0])

x = np.array(x)
y = np.array(y)

x = np.reshape(X, (X.shape[0], X.shape[1], 1))

# ==== LSTM model ====












