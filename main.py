import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import talib as ta
# import time
# import schedule
import pytz
# Import Matplotlib's `pyplot` module as `plt`
# import matplotlib.pyplot as plt

import Util
import Utils


# Main variables
time_frame = mt5.TIMEFRAME_M15
time_frame_big = mt5.TIMEFRAME_H1
# symbol = "AUDNZD"
symbol = "USDCAD"


if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())


df = Utils.get_data(symbol, time_frame)
df_big = Utils.get_data(symbol, time_frame_big)

print("GET DATA DONE")

df = Utils.add_orders(df, df_big)
print("ADD ORDERS DONEE")

df = Utils.add_exec_prices(df)
print("ADD EXEC PRICES DONE")

df = Utils.add_calculations(df)
print("ADD CALCULATIONS")


print("return :", df.Return.sum())

print("POS :", df.pos.sum())

print("NEG :", df.neg.sum())

print("SUM of POS and NEG = ",df.pos.sum() + df.neg.sum())

df.to_excel("excel/second-plz.xlsx", sheet_name='Sheet 1')



print("JOB IS DONEE")

'''
get_data
add_orders
add_exec_prices
add_calculations
'''
