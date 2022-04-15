# Manages gathering of information and statistics to be used for debugging and future analytics, saves data to various logs

# errors
# If any command fails on client side
# all client side errors
# all server side errors

# info
# any command succeeds
# any action taken by the trade boi (closing positions, etc.) 

# data
#   [ 
#     collect 7 candles on each entry, where candle 0 is the entry candle and 6 is the most distant. Each candle has HLOC, Vol, distance to emalong,atr
#     time of entry candle, symbol, side
#     max distance reached (max - open / open - max) after 21 bars
#     outcome of trade after 21 bars
#   ]

import os
from datetime import date, datetime
import pytz
from collections import namedtuple

Block = namedtuple('Block', 'keys, values')

class Report:

    def __init__(self, title):
        self.title = title # Symbol_Type
        self.data = None
    
    def save(self):
        # Save data to new or existing file of name title
        os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\data')
        f = open(self.title +".txt",'a')

        today = date.today()
        format_date = today.strftime("%b-%d-%Y")
        f.write(format_date+" ")

        tz_NY = pytz.timezone('America/New_York') 
        datetime_NY = datetime.now(tz_NY)
        f.write("NY time: " + datetime_NY.strftime("%H:%M:%S")+" ")

        tz_London = pytz.timezone('Europe/London')
        datetime_London = datetime.now(tz_London)
        f.write("London time: " + datetime_London.strftime("%H:%M:%S"))
        f.write('\r\n')

        if len(self.data.keys) == len(self.data.values):
            for k, v in zip(self.data.keys, self.data.values):
                f.write(k + ", " + str(v)+"\r\n")
        else:
            for k in self.data.keys:
                f.write(k)

        # Clear report
        f.close()

    def add(self, keys, values):
        self.data = Block(keys, values)

class Info:
    def __init__(self, title):
        self.title = title
        self.block = Block([], [])
    def add(self, key, value):
        self.block.keys.append(key)
        self.block.values.append(value)
    # Check for successes [OK's returned by client side]
    def find(self, key):
        for k, v in zip(self.block.keys,self.block.values):
            val = v.split(":")
            if k == key and int(val[0]) < 99:
                return 1
            else:
                return -1
        return 0
    def compile(self):
        run_report(self.title, self.block)
        self.block = Block([], [])
    def has(self):
        return len(self.block.keys) > 0

def run_report(title, data):
    r = Report(title)
    keys = data[0]
    try:
        values = data[1]
    except:
        values = []

    r.add(keys, values)
    r.save()


# r = Report("USDJPY_Test")
# r.add( ["high", "open", "low"], [1.0001, 1.000, 0.9996]) 
# r.save()

#run_report("USDJPY_Test", [["Test is successful"]])

# i = Info("USDJPY_Test")
# i.add("Error", "You are a bitch nigger.")
# i.add("Info", "I lied, you are a hero.")
# i.add("Candle1_height", 0.1)
# i.compile()