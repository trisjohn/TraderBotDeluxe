# Holds all data structures for the brain
import os
from collections import namedtuple
import json
import numpy as np
import datetime
from datetime import datetime as dt
from datetime import timedelta as td
####

# IMPORTANT! THIS ALL NEEDS TO BE CONVERTED TO NUMPY!
#

###

position = np.dtype([('side', 'S4'),('ticket1', np.int32), ('ticket2', np.int32), ('opentime', 'datetime64[ms]'), ('closetime', 'datetime64[ms]'), ('outcome', '<f4')]) # outcome is distance from open to close / atr of open
tick = np.dtype([('type', 'S3'), ('price', np.float64), ('time', 'datetime64[ms]')]) # type is ask/bid
candle = np.dtype([('high', np.float64), ('low', np.float64), ('open', np.float64), ('close', np.float64), ('timeopen', 'datetime64[ms]'), ('timeclose', 'datetime64[ms]')])
def write(name, data, typ='w'):
    os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')
    with open(name, typ+'b') as f:

        np.save(f, data)

# Parse a numpy array (position) from a string
# side,ticket1,ticket2,opentime,closetime,outcome
def new_position(string):
    arr = string.split(",")
    if len(arr) != 6: raise Exception(arr, "\r\n<String to parse for new position is false>\r\n", string)
    return (arr[0], int(arr[1]), int(arr[2]), np.datetime64(int(arr[3]),'ms'), np.datetime64(int(arr[4]), 'ms'), float(arr[5]))

# TESTS

# a, b, c, d, e, f = new_position("buy,10798,109935,122222,255555,234.56")
# print(a,b,c,d,e,f)


def read(name):
    os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')
    data = np.load(name, allow_pickle=True)
    print("Reading numpy data...", len(data))
    return np.append([],data)


# TEST THIS
def update(name, data):
    updated = np.array([], dtype=position)
    old = read(name)
    for o in np.nditer(old):
        for d in np.nditer(data):
            if o['ticket1'] == d['ticket1'] or o['ticket2'] == d['ticket2']:
                updated = np.append(updated, d)
            else:
                updated = np.append(updated, o)
    write(name, updated, 'w')
    return updated

# convert a txt file to numpy array. Assumes json format.
def convert(name, t=tick):
    os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')
    data = np.array([], dtype=t)
    with open(name, 'r') as f:
        for x in f:

            d = json.loads(x.strip())
            if t == tick:
                typ = d['type']
                price = np.float64(float(d['value']))
                tim = np.datetime64(int(d['time']), 'ms')
                print(type(typ), type(price), type(tim), data)
                data = np.append(data, [(typ, price, tim)])
    return data

# clean a txt file (works as a find and replace)
def clean(name,error, fixed=""):
    os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')

    f = open(name, 'r')
    data = []
    for d in f:
        
        if d.count(error) > 1:
            print("x",end="")
        if d.count(error) == 1:
            temp = d.replace(error,fixed)
            data.append(temp)
        else:
            data.append(d)

    f.close()

    f = open(name, 'w')
    for d in data:
        f.write(d)
    
    f.close()

def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    ema = np.array([])
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema = np.append(ema, [sma])

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema = np.append(ema, [( (s[n] - sma) * multiplier) + sma])

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema = np.append(ema, tmp)

    return ema

# Tests
# current_time = dt.now()
# data = np.array([('ask', 11.75,np.datetime64(current_time.isoformat())),('bid', 11, np.datetime64(current_time.isoformat()))], dtype=tick)
# for i in range(10):
#     current_time = dt.now() - td(seconds=i)
#     current_time = np.datetime64(current_time.isoformat())

#     data = np.append(data,[('ask', 12.00+(i*.05),current_time),('bid', 11.5+(i*.05), current_time)])

# current_time = dt.now().isoformat()
# data = np.array([('buy',1027, 1029, current_time,None,0)], dtype=position)
# write("test", data, 'w')

# close_time = (dt.now() + td(hours=6)).isoformat()
# data = np.array([('buy',1027, 1029, current_time,close_time,726.26)], dtype=position)
# print("Update test:",update("test", data))
# t = read("test")
# print(t)
# clean("XAUUSD_tickdata.txt", "ask", '"ask"')
# clean("XAUUSD_tickdata.txt", "bid", '"bid"')
# d = read("XAUUSD_tickdata.txt")
# print(d[0], d[len(d)-1])

