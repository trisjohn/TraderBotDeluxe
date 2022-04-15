# Menu to control trade manager

from lib.thread import *
import datetime, time
from lib.connection import *
from lib.timerlogger import clear_folder
from lib.updater import *
import pandas as pd
import os
from lib.globals import *

def correct_choice(key):
    return input(f"Did you mean to select {key}(y)? > ") == 'y'

## "risk", "stop distance", "take distance", "trade number", "close on line", "target", "max drawdown", "daily loss limit"
def check_input(key, val):
    if key == "symbol":
        return isinstance(val, str) and len(val) == 6
    if key == "buy" or key =="sell":
        return isinstance(val, bool)
    if key == "trade number" or key == "timeframe" or key =="ema short" or key == "ema long" or key == "atr period":
        return isinstance(val, int) and val > 0
    if key == "risk" or key == "stop distance" or key == "take distance" or key == "target" or key == "max drawdown" or key == "daily loss limit":
        return isinstance(val, float) and val > 0

def input_needed(typ, key):
    val = None
    print(f"Checking input {key} on {typ}")
    if typ == "Trade":
        if key == "symbol":
            val = input("Symbol for new entry > ")
        elif key == "buy":
            val = input("Confirm Buy(y) > ") == 'y'
        elif key == "sell":
            val = input("Confirm Sell(y) > ") == 'y'
        elif key == "line":
            if input("Enter on trendline(y)? > ") == 'y':
                d1 = int(input("Day of month of point A (0 if today) > "))
                t1 = input("Time of point A (00:00) > ")
                d2 = int(input("Day of month of point B (0 if today) > "))
                t2 = input("Time of point B (00:00) > ")

                if len(t1) != 5 or len(t2) != 5:
                    raise RuntimeWarning("Time value for line invalid must be 00:00", t1, t2)
                val = []
                val.append([d1,t1])
                val.append([d2,t2])
        elif key == "times":
            d1 = int(input("Day of month of point A (0 if today) > "))
            t1 = input("Time of point A (00:00) [MT4 SERVER TIME] > ")
            d2 = int(input("Day of month of point B (0 if today) > "))
            t2 = input("Time of point B (00:00) [MT4 SERVER TIME]  > ")

            if len(t1) != 5 or len(t2) != 5:
                raise RuntimeWarning("Time value for line invalid must be 00:00", t1, t2)
            val = []
            val.append([d1,t1])
            val.append([d2,t2])
    elif typ == "Manage":
        if key == "risk":
            val = float(input("Input new risk value as decimal or cash value > "))
        elif key == "stop distance":
            val = float(input("Input new stop distance as a multiple of atr > "))
        elif key == "take distance":
            val = float(input("Input new stop distance as a multiple of atr > "))
        elif key == "trade number":
            val = int(input("Number of traders per position > "))
        elif key == "close on line":
            print("Not yet supported.")
        elif key == "target":
            val = float(input("Set a profit target to begin tracking (uses current balance as initial) > "))
        elif key == "max drawdown":
            val = float(input("Set a maximum drawdown as a decimal (tracks highest account balance from this point on) > "))
        elif key == "daily loss limit":
            val = float(input("Set the daily loss limit as a decimal > "))
    elif typ == "Show":
        if key == "account":
            val = input("Select option to run analysis: \r\n> ")
        elif key == "win rate":
            val = input("Select period to run analysis on (y/m/w/d) > ")
        elif key == "average trade":
            val = input("Average loss (l) win (w) or both? > ")
    elif typ == "Market Technicals":
        if key == "timeframe":
            val = int(input("Input time frame (minutes) > "))
        elif key == "atr period":
            val = int(input("Input atr period > "))
        elif key == "ema short":
            val = int(input("input ema short period > "))
        elif key == "ema long":
            val = int(input("input ema long period > "))
    return val

class Option:
    def __init__(self, path, key, values):
        self.key = key
        self.path = path
        self.values = {}
        for v in values:
            self.values[v] = None
        
        self.selected = None
    
    def get_time(self, arr, dt):
        days = arr[0]
        new_dt = dt
        while new_dt.day != days:
            new_dt -= datetime.timedelta(days=1)
        hours_string = arr[1].split(':')
        hours = int(hours_string[0])
        minutes = int(hours_string[1])
        new_dt = new_dt - datetime.timedelta(hours = dt.hour - hours, minutes = dt.minute - minutes, seconds = dt.second, microseconds=dt.microsecond)
        return new_dt
    
    def print_values(self):
        i = 0
        for k,v in self.values.items():
            if i > 2: 
                print("\n")
                i = 0
            print(f"{k} (={v})",end="   ")
            i+=1
        print("")
    
    def save(self):
        """ save option to file """
        os.chdir(self.path)
        o_path = self.key+"_options.csv"
        new_df = pd.DataFrame(self.values, index=[self.key])
        try:
            ### grab current tables and append them to csv file one by one [with open path 'a' as f pd to.csv(f, header=False/True)]
            with open(o_path, 'r') as f:
                print("Reading save file...")
                df = pd.read_table(f)
                print(df)
        except Exception as e:
            print("No current saved options, creating new.", e)
            new_df = pd.DataFrame(self.values, index=[self.key])
        time.sleep(0.5)
        if self.key == 'Trade':
            # Append new trade if trade option saved, these will be read by updater later
            new_df['entrytime'] = datetime.datetime.now()
            with open(o_path, 'a') as f:
                new_df.to_csv(f, sep="\t")
        else:    
            with open(o_path, 'w') as f:
                new_df.to_csv(f, sep="\t")
                print("Option",self.key,"saved.")        
    
    def read(self):
        """ build option from file """
        os.chdir(self.path)
        o_path = self.key+"_options.csv"
        try:
            
            with open(o_path) as f:
                df = pd.read_table(f, engine="python", index_col=0)
                print(df)
                
            ######################### Data file will be multiple tables. iterate through tables until the correct one is found.
            for i, row in df.iterrows():
                if i == self.key:
                    self.values = {}
                    for k,v in row.items():
                        self.values[k] = v
        except Exception as e:
            print(f"Unable to read {self.key} preset options. Please set options and then save them using the 'save' command.", e)
  
    def select(self, s):

        if s == "\r" or s == "" or s =="q" or s == "quit":
            if not self.key == "Trade": return
            val = input("Leave and Wipe current entry?\ny: wipe & leave\nw: wipe & stay\n_: \
                        (anything else) keep current values and exit\n  > ") 
            if  val  == 'y':
                self = Option(self.path,"Trade", ["symbol", "buy", "sell", "line", "times"])
                return
            elif val == 'w':
                self = Option(self.path,"Trade", ["symbol", "buy", "sell", "line", "times"])
            else:
                return
                
                
        if s == "save":
            self.print_values()
            if input("You sure you want to save these values? (y) > ") == "y":
                self.save()
            return
        elif s == "load":
            print("Loading saved settings...")
            self.read()
            self.print_values()
            return
        
        for k in self.values:
            if k.find(s) > -1:
                if correct_choice(k):
                    val = input_needed(self.key,k)
                    if k != 'line' and k != 'times':
                        if not check_input(k, val):
                            print("Invalid input for", k)
                            return
                        print(f"Successful {k} update =>", val)
                        self.values[k] = val
                        continue
                    else:
                        self.values['line'] = True
                        now = datetime.datetime.now()
                        time1 = self.get_time(val[0], now)
                        time2 = self.get_time(val[1], now)
                        self.values['times'] = [time1,time2]

        self.print_values()
        self.select(input(self.key+"--> "))

class Menu:
    def __init__(self):
        # Do a quick search for path, if none found, user can correct later
        print("Searching for directories...")
        path = ""
        for s, _, _ in os.walk(os.curdir):
            if s.find('/metyBoi/lib') >= 0:
                arr = s.split('/metyBoi/lib')
                path = arr[0] + '/metyBoi/lib'
                print("Path found", path)
                break
        self.alive = True
        if path == "":
            while True:
                path = input("Enter path. (Ensure it is the path to the metyBoi\lib) > ")
                if path.find('/metBoi/lib') < 0: 
                    print("Path variable incorrect, please try again.")
                else: 
                    break
        set_path(path)
        self.path = path+'\saves'
        self.choices = [
            Option(path,"Trade", ["symbol", "buy", "sell", "line", "times"]),
            Option(path,"Manage", ["risk", "stop distance", "take distance", "trade number", "close on line", "target", "max drawdown", "daily loss limit"]),
            Option(path,"Show", ["account", "win rate", "average trade", "ROI"]),
            Option(path,"Market Technicals", ["timeframe", "atr period", "ema short", "ema long"])
        ]
        print("Welcome to metyBoi.\r\n")
        print("Establishing Connection to client...")
        
        ### Send a test Json
        self.client = MT4Connection()
        status, self.handler = self.client.check(0)
        if not status:
            print("Error, no connection. Please Kill Menu.")
            self.current_status = "Offline."
        else:
            self.alive = True
        print("Status: ",status)
        self.updater = Updater(self.client, self.path)
        side_thread(900, "Updater", )
        self.start_time = datetime.datetime.now()
    
    def start(self):
        # Runs the menu, returns relevant data of operations
        messages = []
        i = 0
        print()
        
        for c in self.choices:
            i+=1
            print(f"<---{c.key}--->")
        i = input("Select choice > ")
        load_options = False
        if i == "load":
            load_options = True

        if i == "save":
            if input("Save current path? (y) > ") == 'y':
                name = input("Path's name > ")
                if input(f"is {name} correct? (y) > "):
                    with open(f"{name}.txt", 'w') as f:
                        f.write(self.path)
                else:
                    print("Path save canceled.")
            else:
                print("Path save canceled.")

        if i == "wipe":
            if input("Wipe all menu files? (y) > ") == "y":
                clear_folder(self.path)
            return

        if i == "exit" or i == "quit":
            self.alive = False
            return
        found = False
        for c in self.choices:
            if load_options:
                print("Loading option:",c.key)
                c.read()
            if c.key.find(i) > -1:
                if correct_choice(c.key):
                    print("\n__")
                    found = True
                    c.print_values()
                    print("__")
                    c.select(input(f"{c.key} --> "))
                    break
        
        if not found:
            if "exit".find(i) > -1 or "quit".find(i) > -1 or "kill".find(i) > -1:
                if input("Kill Menu and exit metyBoi? (y) > ") == "y":
                    self.alive = False
            elif i == "status" or i == "-s":
                print(self.current_status)
            else:
                print("Try again.")
        
print(__package__, __name__)          