#LSTM is sequence based
import numpy as pd
import os
from sklearn.preprocessing import MinMaxScaler
from keras.models import sequential

# ==== Path Setup ====
stock_symbol = input("Enter stock symbol: ").upper()
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
file_path = os.path.join(base_dir, 'data', 'cleaned', f'{stock_symbol}.xlsx')
df = read.excel(file_path)















