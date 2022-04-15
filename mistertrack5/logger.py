from TradeBoiDeluxe.lib import thread
import datetime
import pandas as pd
import os

class Logger:
    def __init__(self, name):
        self.info = []
        self.codes = [] # info codes [0:ok, 1:warning, 2:important] error codes
        self.times = []
        self.name = name

    def add(self, info, code):
        self.info.append(info)
        self.codes.append(code)
        self.times.append(datetime.datetime.now())

    def save(self):
        os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\mistertrack5\data')
        dict = {'info': self.info, 'code': self.codes, 'time' : self.times}
        data_frame = pd.DataFrame(dict)
        old = pd.read_csv(self.name)
        if not old:
            data_frame.to_csv(self.name)
        else:
            data_frame.to_csv(self.name, mode='a', header=False)
        self.info = []
        self.codes = []
        self.times = []

def log_error(info, code):
    e = Logger("error")
    e.add(info, code)
    thread.side_thread(30,"Error Logger", e.save)

def log(info, code):
    e = Logger("info")
    e.add(info, code)
    thread.side_thread(31,"Info Logger", e.save)
            