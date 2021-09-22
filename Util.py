import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import talib as ta
# import time
# import schedule
import pytz


def get_data(symbol, time_frame):
    data = dict()
    utc_from = datetime(2020, 1, 1, tzinfo=pytz.timezone('Etc/GMT-4'))
    date_to = datetime(2021, 2, 1, tzinfo=pytz.timezone('Etc/GMT-4'))
    rates = mt5.copy_rates_range(symbol, time_frame, utc_from, date_to)
    df = pd.DataFrame(rates)  
    #conver teh fime column to a readable format
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    #create the change column
    df['change'] = df.apply(lambda row: row.open - row.close, axis = 1) 
    # calculate and add EMAs to data frame
    df['8ema'] = ta.EMA(df['close'], 8)
    df['13ema'] = ta.EMA(df['close'], 13)
    df['21ema'] = ta.EMA(df['close'], 21)
    # df = add_orders(df)
    
    return df

""" 
    this is the idea of 2 time frames backtest 

    df_small_time_frame = get_data(symbol, small_time_frame)
    df_big_time_frame = get_data(symbol, big_time_frame)

    and the add_order() function should now take 2 dataframes as parameters
    one for the small time_frame and the second for the big time_frame

"""
   
"""
    logic 
    if i % 4:
        # this condition means that 4 candles has been added in the small time_frame (in case of 15 min)
        # this is when one candle is added on the big time_frame (in case of 1 hour) 

    example
    k=21 # k is the index of the bigger time frame df
    for i in range(len(df_small["close"])): 
        if i > k*4: 
            
            if i % 4:
                k += 1


"""
   

def add_orders(df, df_big):
    # add the maker execution depending on the conditions buy and sell
    new_column = [None] * len(df["close"])  # create new column
    buy = 'buy - closing short position'
    sell = 'sell - closing long position'
    count_buy = 0
    count_sell = 0
    k = 21
    s = k*4
    for i in range(len(df["close"])):
        
        if i > s:

            if i % 4:
                k += 1

            mov_avg8_big = df_big['8ema'][k]
            mov_avg13_big = df_big['13ema'][k]
            mov_avg21_big = df_big['21ema'][k]

            trendup = mov_avg8_big >= mov_avg13_big and mov_avg13_big >= mov_avg21_big
            trenddown = mov_avg8_big <= mov_avg13_big and mov_avg13_big <= mov_avg21_big
            
            mov_avg8 = df['8ema'][i]
            mov_avg13 = df['13ema'][i]
            mov_avg21 = df['21ema'][i]
            
            low = df['low'].iloc[i]
            high = df['high'].iloc[i]
            
            mov_avg8_prev = df['8ema'][i-1]
            mov_avg13_prev = df['13ema'][i-1]
            mov_avg21_prev = df['21ema'][i-1]
            
            
            
            prev_trendup = mov_avg8_prev > mov_avg13_prev and mov_avg13_prev > mov_avg21_prev
            prev_trenddown = mov_avg8_prev < mov_avg13_prev and mov_avg13_prev < mov_avg21_prev
            
            # BUY PART
            buy_1 = (mov_avg8 > mov_avg13) and (mov_avg8_prev <= mov_avg13_prev) and trendup
            buy_2 = (mov_avg8 > mov_avg13 and mov_avg13 > mov_avg21 and low > mov_avg8) and not(mov_avg13_prev > mov_avg21_prev)# and trendup
            
            # SELL PART
            sell_1 = (mov_avg8 < mov_avg13) and (mov_avg8_prev >= mov_avg13_prev) and trenddown
            sell_2 = (mov_avg8 < mov_avg13 and mov_avg13 < mov_avg21 and high < mov_avg8) and not(mov_avg13_prev < mov_avg21_prev)# and trenddown
            
            
            if buy_1 or buy_2:
                new_column[i] = buy
                count_buy  +=1
                
            elif sell_1 or sell_2:
                new_column[i] = sell
                count_sell +=1

    print(new_column)
    df["exec"] = new_column  # add new column
    print(count_buy , ' buy orders')
    print(count_sell, ' sell orders')
    
    return df

def add_exec_prices(df):
    buy_column = [None] * len(df["close"])
    sell_column = [None] * len(df["close"])
    buy = 'buy - closing short position'
    sell = 'sell - closing long position'
    count_buy = 0
    count_sell = 0
    
    for i in range(len(df["close"])):  
        if i > 21:
            if df["exec"][i] == buy :
                buy_column[i] = df["close"][i]
                count_buy +=1
                
            elif df["exec"][i] == sell:
                sell_column[i] = df["close"][i]
                count_sell +=1
                
            else:
                buy_column[i] = None
                sell_column[i] = None
        
        df['exec_buy'] = buy_column
        df['exec_sell'] = sell_column
    
    print(count_buy)
    print(count_sell)
        
    return df

def add_calculations(df):
    # add the maker execution depending on the conditions buy and sell
    highest_column = [None] * len(df["close"])  # create new column
    lowest_column = [None] * len(df["close"])  # create new column
    return_column = [None] * len(df["close"])  # create new column
    
    pos_column =  [None] * len(df["close"])  # create new column
    neg_column = [None] * len(df["close"])  # create new column
    open_pos_price = [None] * len(df["close"])  # create new column
    PnL_column = [None] * len(df["close"])  # create new column
    
    percentage_change_high = [None] * len(df["close"])  # create new column
    percentage_change_low = [None] * len(df["close"])  # create new column
    percentage_change_close = [None] * len(df["close"])  # create new column
    
    
    buy = 'buy - closing short position'
    sell = 'sell - closing long position'
    # count_buy = 0
    # count_sell = 0
    for i in range(len(df["exec"])):
        
        if i > 21:
            first_entry = 0
            # if its a long (buy to sell)
            if df["exec"][i] == buy:
                # i buy row
                high_in_between = []
                low_in_between = []
                j = i+1
                # j closing row
                while j > i:
                    high_in_between.append(df["high"][j])
                    low_in_between.append(df["low"][j])
                    
                    if df['exec'][j] == sell:
                        long = df["close"][i]
                        open_pos_price[j] = long

                        highest_high = max(high_in_between)
                        highest_column[j] = highest_high
                        lowest_low = min(low_in_between)
                        lowest_column[j] = lowest_low

                        # calculate profit this
                        # closing position price - buy position price
                        PnL = df["close"][j] - long
                        return_column[j] = PnL

                        # %change high = (highest - long) / long
                        percentage_change_high[j] = (highest_high - long) / long
                        # %change low = (lowest - long) / long
                        percentage_change_low[j] = (lowest_low - long) / long
                        # %change close = (close - long) / long
                        percentage_change_close[j] = PnL / long

                        if PnL > 0:
                            PnL_column[j] = "P"
                            pos_column[j] = PnL
                        elif PnL < 0:
                            PnL_column[j] = "L"
                            neg_column[j] = PnL
                        else:
                            PnL_column[j] = "neutral"
                            
                        break
                        
                    elif j == len(df["exec"])-1:
                        break
                        
                    j += 1

            
            # if its a long (buy to sell)
            if df["exec"][i] == sell:
                high_in_between = []
                low_in_between = []
                j = i+1
                while j > i:
                    high_in_between.append(df["high"][j])
                    low_in_between.append(df["low"][j])
                    
                    if df['exec'][j] == buy:
                        short = df["close"][i]
                        open_pos_price[j] = short

                        highest_high = max(high_in_between)
                        highest_column[j] = highest_high
                        lowest_low = min(low_in_between)
                        lowest_column[j] = lowest_low

                        # calculate profit this
                        # closing position price - buy position price
                        # profit = df["close"][j] - df["close"][i]
                        PnL = short - df["close"][j]
                        return_column[j] = PnL

                        # %change high = -(highest - short) / short
                        percentage_change_high[j] = -(highest_high - short) / short
                        # %change low = -(lowest - short) / short
                        percentage_change_low[j] = -(lowest_low - short) / short
                        # %change close = -(close - short) / short
                        percentage_change_close[j] = PnL / short

                        if PnL > 0:
                            PnL_column[j] = "P"
                            pos_column[j] = PnL
                        elif PnL < 0:
                            PnL_column[j] = "L"
                            neg_column[j] = PnL
                        else:
                            PnL_column[j] = "Na zero"
                            
                        break
                        
                    elif j == len(df["exec"])-1:
                        break
                    
                    j += 1                           
                            
    df["Highest"] = highest_column
    df["Lowest"] = lowest_column
    df["Return"] = return_column
    df["P/L"] = PnL_column
    df["Open Position Price"] = open_pos_price
    df["pos"] = pos_column
    df["neg"] = neg_column
    df["highest percentgge change"] = percentage_change_high
    df["lowest percentage change"] = percentage_change_low
    df["close percentage change"] = percentage_change_close
    
    return df