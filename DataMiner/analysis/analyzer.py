import pandas as pd
import numpy as np


class Analyzer:
    """
    Takes in a panda array and a list of tuple arguments:
        ('EMA', int period on close), 
        ('Rel_High', int for max high over period eg. 17 or str of time val eg. "240Min")
        ('Rel_Low', int for min low over period eg. 17 or str of time val eg. "240Min")
        ('VWAC', int for period eg. 17 or 0 for day : checks volume per close)
        ('ATR', int for period)
    """
    def __init__(self, df, args):
        self.data = df
        for name, val in args:
            if name == "EMA":
                self.add_ema(val)
            elif name == "Rel_High":
                self.relative_max(val, False)
            elif name == "Rel_Low":
                self.relative_max(val)
            elif name == "VWAC":
                self.vol_weighted_avg_close(val)
            elif name == "ATR":
                self.add_atr(val)
    
    def add_atr(self, val):
        """
        Fills a column on the data frame that will be the atr for the given period.
        """
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self.data['high'] - self.data['close'].shift())
        low_close = np.abs(self.data['low'] - self.data['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)

        atr = true_range.rolling(val).sum()/val
        atr.fillna(0,inplace=True)
        self.data['ATR'] = atr


    def vol_weighted_avg_close(self, period):
        """
        Fills a column on the data frame that represents the volume-weighted-avg close for the period
        This is calculated by summing each close * volume for a period, dividing that sum by the sum of volumes over that period
        """
        if period == 0:
            distance = pd.Timedelta(self.data.index[1] - self.data.index[0]).seconds / 60
            period = round(2440 / distance)
        values = []
        closes = self.data['close'].iloc[::-1]
        volumes = self.data['volume'].iloc[::-1]
        for i in range(0,len(closes), period):
            vol_sum = volumes[i:i+period].values.sum()
            adj_sum = (closes[i:i+period].values * volumes[i:i+period].values).sum()
            vwac = adj_sum/vol_sum
            if len(values) < len(closes) - period:
                values.extend([vwac for _ in range(period)])
            else:
                values.extend([vwac for _ in range(len(closes) - len(values))])
                break
        new_values = pd.Series(values, index=closes.index)
        self.data[f"VWAC {period}"] = new_values.iloc[::-1]
        print(f"VWAC {period} added to dataframe.")
        print(self.data.head(1))
        print(self.data.tail(1))
            


    def add_ema(self, period):
        self.data[f"EMA {period}"] = self.data['close'].ewm(span=period, adjust=False).mean()
        print(f"EMA {period} added.")
        print(self.data.head(1))
        print(self.data.tail(1))

    def relative_max(self, period, lows=True):
        """
        Find the relative low for the given period for each data point in data, then add it as a column
        """
        is_time = False
        if isinstance(period, str):
            is_time = True
            period = int(period.split("Min")[0])
        
        if is_time:
            distance = pd.Timedelta(self.data.index[1] - self.data.index[0]).seconds / 60
            period = period / distance

        values = []
        if lows:
            low_arr = self.data['low'].iloc[::-1]
            for i in range(0,len(low_arr), period):
                low = low_arr[i]
                for x in low_arr[i:i+period]:
                    if x < low:
                        low = x
                values.extend([low for _ in range(period)])
            if len(values) != len(low_arr):
                raise Exception("Relative low computation failed", values[:20])
            new_values = pd.Series(values, index=low_arr.index)
            self.data[f'Relative Low {period}'] = new_values.iloc[::-1]
            print("Relative lows saved")
        else:
            high_arr = self.data['high'].iloc[::-1]
            for i in range(0, len(high_arr), period):
                high = high_arr[i]
                for x in high_arr[i:i+period]:
                    if x > high:
                        high = x
                values.extend([high for _ in range(0,period)])
            if len(values) != len(high_arr):
                raise Exception(f"Relative high computation failed {len(values)} should be {len(high_arr)}", values[:20])
            new_values = pd.Series(values, index=high_arr.index) 
            self.data[f'Relative High {period}'] = new_values.iloc[::-1]
            print("Relative highs saved")
        print(self.data.head(1))
        print(self.data.tail(1))

        
        