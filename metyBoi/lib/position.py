import pandas as pd
import os
from lib.globals import *

class Position:
    """
        [ Position
            A Position object completes with the following data: closetime profit pre-candles maxpositive maxnegative
            close time is used to find the values for pre-candles, maxpositive, and maxnegative directly from server
        ]
        Tickets [##,##] [0] is always the ticket that has a take profit, [1] is the runner
    """
    def __init__(self, side, symbol, tickets, open_time, avg_price, volume, volatility):
        self.side = side
        self.symbol = symbol
        self.tickets = tickets
        self.open_time = open_time
        self.avg_price = avg_price # average the prices of both tickets
        self.volume = volume
        self.volatility = volatility # ATR at open time
        self.open_save()
        self.stop = 0
        ## These variables are saved after the position closes
        self.profit = 0 # constantly updated
        self.pre_candles = []
        self.max_positive = 0 # Max distance in profit between open time and close / volatility
        self.max_negative = 0 # Max distance out of profit between open time and close / volatility
        self.close_time = 0
    
    def open_save(self):
        """ Save the initial values of the position (in case of client crash, etc., to keep track of position data)
        """
        os.chdir(file_path)
        ticket_string = str(self.tickets[0]) + ":" + str(self.tickets[1])
        data = {
            'symbol':self.symbol,
            'side':self.side,
            'tickets': ticket_string,
            'open time': self.open_time,
            'atr': self.volatility,
        }

        try:
            i = pd.read_table('/position_data/open.csv').index.max()
        except:
            i = 0
        df = pd.DataFrame(data, index=[i])
        
        try:
            with open('/position_data/open.csv', 'a') as f:
                df.to_csv(f, sep="\t", header= i==0)

        except Exception as e:
            print(f"Error when trying to save newly opened position: {e}")


    def update(self, data, vars):
        """ update position with a data dictionary of:
            tickets: [], profit: #, ask: #, bid: #, low: #, high: #, last close: #, mean=#
            
            and a variable dict of: take dist: #, trail dist:#, even dist:#, stop dist:#
            where # is a multiple of self.volatility

            return a dictionary of:
            exit: [] (tickets to close), stop: 0 or (new stop)

            Note: self.stop is a virtual stop and will check if price crosses and force an exit, it is not updated by nor does it
            care for the current stop order on the trade server
        """
        res = {
            'exit': [],
            'stop': 0
        }
        stop_dist = vars['stop dist'] * self.volatility
        even_dist = vars['even dist'] * self.volatility
        take_dist = vars['take dist'] * self.volatility
        trail_dist = vars['trail dist'] * self.volatility

        if self.stop == 0:
            dist = stop_dist
            self.stop = self.avg_price - dist if self.side == 0 else self.avg_price + dist

        old_stop = self.stop

        for k,v in data.items():
            if k == 'tickets':
                self.tickets = v
                if self.tickets[0] == -1:
                    print(f"Position {self.symbol} target reached.")
            elif k == 'profit':
                self.profit = v
            elif k == 'ask' or k == 'low':
                if self.side == 0:
                    if v <= self.stop:
                        res['exit'].extend(self.tickets)
                    elif v - self.stop >= trail_dist:
                        self.stop = v
                elif self.side == 1: 
                    if v <= self.avg_price - take_dist:
                        # If ticket 1 is not closed even tho target has been hit, close it out
                        res['exit'].append(self.tickets[0]) if self.tickets[0] > 0 else None
                        self.stop = self.avg_price - even_dist if self.avg_price - even_dist < self.stop else self.stop
                     
            elif k == 'bid' or k == 'high':
                if self.side == 1:
                    if v >= self.stop:
                        res['exit'].extend(self.tickets)
                    elif self.stop - v >= trail_dist:
                        self.stop = v
                elif self.side == 0 and v >= self.avg_price + take_dist:
                    res['exit'].append(self.tickets[0])
                    self.stop = self.avg_price + even_dist if self.avg_price + even_dist > self.stop else self.stop
            elif k == 'last close':
                # close order if in profit and closes beyond mean
                if self.side == 0 and self.tickets[0] == -1 and v < vars['mean']:
                    res['exit'].append(self.tickets[1])
                elif self.side == 1 and self.tickets[0] == -1 and v > vars['mean']:
                    res['exit'].append(self.tickets[1])
        
        if old_stop != self.stop:
            res['stop'] = self.stop
        
        return res

    def close_and_save(self, data):
        """ After a position is COMPLETELY closed
            load a dictionary of:
            ***pre-candles : [] (an array of candle objects where the first candle is the candle just before the open time of the position)
            ***max positive: max distance in the money the position reached from open to close
            ***min negative: min distance in the money the position reached from open to close
            close time: dt
            final profit: #
            ***BETA: Only saves close time and final profit for the time being.***
        """
        os.chdir(file_path)

        ### Save pre candle data to its own /position_data/candles/#.csv, (where # corresponds to position #)

        try:
            i = pd.read_table('/position_data/closed.csv').index.max()
        except:
            i = 0

        dat = {
            "close time": data['close time'],
            "final profit": data['profit']
        }

        df = pd.DataFrame(dat, index=[i])

        try:
            with open('/position_data/closed.csv', 'a') as f:
                df.to_csv(f, sep="\t", header= i==0)

        except Exception as e:
            print(f"Error when trying to save new closed position: {e}")

                    

    