import duka.app.app as import_ticks_method
from duka.core.utils import TimeFrame
import datetime
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplfinance as mpl 
import os
from DataMiner.trends import *
# from DataMiner.draw import *

###
"""
    To do: 

"""
###

def gather(start_date, end_date, symbols, folder):
    """
    Gather all tick data from start_date to end_date for the given symbols, then save to csv file per each individual symbol
    """
    import_ticks_method(symbols, start_date, end_date, 1, TimeFrame.TICK, folder, True)

def get_tick_data(filename):
    tick_data = pd.read_csv(filename, index_col=["time"], usecols=["time", "ask", "bid", "ask_volume", "bid_volume"], parse_dates=["time"])
    tick_data['volume'] = tick_data['ask_volume'] + tick_data['bid_volume']

    print(tick_data.head(1))
    return tick_data

def ticks_to_candle(df, df_col, tf):
    """
    Convert tick data to candle data given a data column (ask/bid) and a time frame ex "240Min"
    """
    data_frame = df[df_col].resample(tf).ohlc()
    data_frame.index.name = 'date'
    data_frame.dropna(inplace=True)
    print(tf, "candles created.")
    print(data_frame.head(1))
    print(data_frame.tail(1))
    return data_frame

def ticks_to_volume(df, tf):
    """
    Convert tick volume to the timeframe tf
    """
    data_frame = df['volume'].resample(tf).sum()
    print(data_frame.head(1))
    return data_frame

def save_candles(df, symbol, timeframe):
    """
    Saves pandas dataframe that is in candle format
    """
    if not 'open' in df.columns or not 'close' in df.columns or \
    not 'high' in df.columns or not 'low' in df.columns:
        raise Exception("Dataframe passed to save as candle is not ohlc data.")
        
    try:
        begin_date = str(df.index[0]).replace(":", "+")
        end_date = str(df.index[-1]).replace(":", "+")
        df.to_csv(f"{symbol}_candles_{timeframe}_{begin_date}-{end_date}.csv",index=True)
    except Exception as e:
        print("failed to save candle data for", symbol, e)

def show(candles, timeframe, symbol):
    
    print("Plotting candle data", len(candles), candles.head(1), candles.tail(3))
    title = f"{symbol} {timeframe} Candles"

    if candles.shape[1] > 5:
        print("Extra Analysis deteced, building subplots.")
        cols = candles.columns
        extra = candles[[cols[x] for x in range(5, len(cols))]]
        candles.drop([cols[x] for x in range(5, len(cols))], axis=1, inplace=True)
        print("\r\nCandles prepared for plotting...")
        print(candles.head(1))
        print(candles.tail(1))
        adplot = mpl.make_addplot(extra, linestyle='dashdot')
        print("\r\nExtras added to plots.")
        print(extra.head(1))
        print(extra.tail(1))

    mpl.plot(candles,type='candle',volume=True, show_nontrading=False,figratio=(18,10), tight_layout=True, title=title, addplot=adplot)

# tests
# gather(datetime.date(2021,5,1), datetime.date(2021,5,8), ["EURUSD", "AUDNZD"])
# raw_ticks = get_tick_data("TradeBoiDeluxe\DataMiner\symbols_data\AUDNZD-2021_05_01-2021_05_08.csv")
# candles = ticks_to_candle(raw_ticks, "ask", "240Min")

# low_trends = get_low_swing_trends(candles)

# candles['volume'] = ticks_to_volume(raw_ticks, "240Min")
# show(candles, low_trends)