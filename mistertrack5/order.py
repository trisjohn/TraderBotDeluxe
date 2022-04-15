# Holds all order managing classes

from mistertrack5.account import *
from mistertrack5.position import *

class OrderManage:
    def __init__(self, number, s):

        self.actual_risk = 0

        # Change Take
        if number == 1:
            self.take = float(s)
        # Change Stop
        elif number == 2:
            self.stop = float(s)
        # Change Trail
        elif number == 3:
            self.trail = float(s)
        # Change Break Even
        elif number == 4:
            self.even = float(s)
        # Change Risk Value
        elif number == 5:
            self.risk = float(s)  
        # Close at next negative bar close [ buy: close < open, high < lasthigh, sell: close > open, low > lastlow ]
        elif number == 6:
            BeginCounterClose(s)
        # Close position on a trendline cross given a (time1, price1) and a (time2, price2), sells pos use highs at given time, buy pos use lows at given time
        elif number == 7:
            val = s.split(":")
            # time1, time2
            BeginLineClose(time_at(val[0]), time_at(val[1]))

    def update(self):
        # update risk value
        if self.risk > 1:
            self.actual_risk = self.risk / Account().free()
          

class OrderEntry:
    def __init__(self, number, s):

        # Buy
        if number == 1:
            BeginPositionEntry(0, s)
        # Sell
        elif number == 2:
            BeginPositionEntry(1, s)

        # Open entry on a trendline cross given a (time 1, price 1) and a (time2, price2), enters sell on lows and buys on highs
        elif number == 3:
            val = s.split(":")
            # side, time1, time2
            BeginLineEntry(int(val[0]), time_at(val[1]), time_at(val[2]))
        
def time_at(s):
    arr = s.split(":")
    year = int(arr[0])
    day = int(arr[1])
    month = int(arr[2])
    hour = int(arr[3]) # if left 0 gives day candle value
    minute = int(s[4]) # if left 0, gives hour candle value
    dt = datetime.datetime(year=year, day=day,month=month,hour=hour,minute=minute)
    return dt