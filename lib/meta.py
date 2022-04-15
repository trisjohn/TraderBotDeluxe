# Middleman to interact with server and data

"""
    TO DO:

    Fix lot calculations

"""

import os
from collections import namedtuple

from lib.data import *
from lib.report import *
from lib.thread import *
from pathlib import Path

from lib.server import *

Order = namedtuple('Order', 'symbol, side, vol, sl, tp')
Command = namedtuple('Command', 'title args')
Stop = namedtuple('Stop', 'symbol side price dead') # When ask/bid is below/above price on symbol, exit trade
def read_symbols(path):
    obj = []
    os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\data')
    f = open(path, "r")
    for d in f:
        obj.append(d.strip())
    f.close()
    return obj

class Meta:
    def __init__(self):
        self.risk = .05
        self.stop_dist = 3.5
        self.break_dist = 1
        self.trail_dist = 2
        self.take_dist = 2.5
        self.data = Data(self.take_dist,self.stop_dist, self.risk)
        self.managing = False
        self.atr_period = 96
        self.short_period = 9
        self.long_period = 55
        self.time_frame = 15
        self.sleep = False
        self.is_connected = True
        self.info = Info("Info")
        self.errors = Info("Errors")
        self.analysis = Info("Analysis")
        self.server_thread = None
        self.curr_commands = []
        self.symbol_queue = []
        self.stop_orders = []
        self.thread_count = 0
        self.server = Server()
        self.watchlist = read_symbols("watchlist.txt")

    def handle_errors(self, errors):
        for e in errors.value:
            if e != "OK":
                self.errors.add("Order Error", e)
        
        if self.errors.has():
            print("Errors found! Saving to file...") 
            self.errors.compile()

    def run_server(self):
        if self.sleep:
            self.sleep = False
            print("Server resting.") 
            return False # Let server rest inbetween calls
        if not self.server_thread:
            self.server_thread = NewThread(99, "Server", self.check_server)
            self.server_thread.start()
        elif not self.server_thread.is_alive():
            self.server_thread = None
            self.sleep = True
            return True #Server completed
        return False # Server still runnning

    def check_server(self):
        if len(self.curr_commands) < 1: return
        for c in self.curr_commands:
            self.server.new_command(c.title, c.args) if c.args else self.server.new_command(c.title)

        command = new_thread(90, "Command Handler", self.server)
        print("Server finished. Gathering Data...")
        acc, position, symbol, error = self.server.get_data()
        if command.is_alive():
            print("Command thread is still alive.")
            self.server.reset_settings()
            return
        else:
            self.curr_commands = [] # reset all commands
        if acc:
            self.data.update_account(acc.value)
            data = self.data.account.search("equity")
            print("Saving account data. Current Equity =", data)
        if position:
            self.managing = self.manage_positions(position.value)
        if symbol:
            self.data.update_market(symbol)
            for s in self.data.market.value:
                print(s.key, "Market data updated. Last Close:", s.search("close"))
        if error:
            print("Errors colllected!", error)
            self.handle_errors(error)
        print("Server check completed.")
        
        # If no data is being gathered, most likely there is not a connected client
        if not acc and not position and not symbol and not error:
            self.is_connected = False
            return
        self.is_connected = True

    def current_profit(self):
        if not self.data.account: return "xx.xx"
        return str(self.data.account.search("profit"))

    def is_close(self, symbol):
        # Match symbol to that within the saved managements
        # -> symbol, side, price
        trigger = False
        for s in self.stop_orders:
            if s.dead:
                print("Stop triggered and completed.")
                self.stop_orders.remove(s)
                continue
            if s.symbol == symbol:
                trigger = self.data.stop_triggered(symbol, s.side, s.price)
                if trigger:
                    s = Stop(s.symbol, s.side, s.price, True)
                    print("triggered stop at", s)
                return trigger

        return False

    def is_new_stop(self, stop):
        for s in self.stop_orders:
            if stop.symbol == s.symbol:
                return stop.price > s.price if stop.side == 0 else stop.price < s.price

        return True        

    def manage_positions(self, d):
        isChange = False
        print("Position data gathered.") if len(d) > 0 else None
        if len(d) == 0: return
        self.data.update_positions(d, self.take_dist)
        alive_symbols = [] # Save all position symbols that are alive, delete any stop orders for non-exisitng positions
        for p in self.data.manage_positions(self.break_dist, self.trail_dist):
            if isinstance(p, str):
                self.fetch_market(p)
                continue
            s, side, b, t, e = p
            to_close = self.is_close(s)
            alive_symbols.append(s)
            self.fetch_market(s)
            if not self.data.check_market(s):
                print("Error, market data missing or corrupt.")
                return 
            if e or to_close :
                self.new_command("close", [s])
                print("Exit signaled!", s)
                isChange = True
                continue
            if b > 0:
                new_stop = Stop(s,side,b, False)
                if self.is_new_stop(new_stop): 
                    self.stop_orders.append(new_stop)
                self.new_command("modify", [s, b])
                print("Break Even signaled!", s)
                isChange = True
                continue
            if t > 0:
                new_stop = Stop(s,side,b, False)
                if self.is_new_stop(new_stop): 
                    self.stop_orders.append(new_stop)
                self.new_command("modify", [s, t])
                print("Trail stop signaled!", s)
                isChange = True
        for s in self.stop_orders:
            is_alive = False
            for a in alive_symbols:
                if s.symbol == a:
                    is_alive = True
            if not is_alive: self.stop_orders.remove(s)
        return isChange

    def new_command(self, title, args=None):
        com = Command(title,args) if not isinstance(title, Command) else title
        try:
            if com.title != "buy" and com.title != "sell":
                self.curr_commands.remove(com)
                print("Removed duplicate", title)
            else:
                print("order command detected.", com.title)
        except:
            print("New server command added", title)
            
        self.curr_commands.append(com)
        
    def edit_risk(self, val):
        self.risk = val / 100
    
    def edit_stop(self, val):
        self.stop_dist = val * 0.25
    
    def edit_take(self, val):
        self.take_dist = val * 0.25

    def fetch_all_markets(self):
        print("Fetching all market data.")
        for x in self.watchlist:
            self.fetch_market(x)
        print("All market data fetched.")

    # Construct a new order using current market conditions for the given symbol
    def build_order(self, side, symbol):
        market = self.data.market.search(symbol)
        if not market:
            print("Error no market found when trying to build order.")
        print("Building new order for market:", market.search("atr"))
        price = market.search("ask") if side == 0 else market.search("bid")
        atr = market.search("atr")
        digits = market.search("digits")
        stop = price - self.stop_dist * atr if side == 0 else price + self.stop_dist * atr
        print("Stop calculated.",stop)
        stop = flat_float(stop, digits)
        take = price + self.take_dist * atr if side == 0 else price - self.take_dist * atr
        print("take calculated.",take)
        take = flat_float(take, digits)
        vol = self.calculate_lots(price, stop, market)
        print("volume calculated", vol)
        if vol > market.search("maxlot"): vol = market.search("maxlot")
        if vol < 0.01: vol = 0.01
        return Order(symbol,side,vol,stop, take)

    def fetch_market(self, symbol=None):
        if not symbol:
            symbol = self.data.entry.search("symbol")
        if not symbol:
            print("CRITICAL ERROR! Fetching market for entry, but entry has no symbol")
            return
        print("Fetching Market info for", symbol, str(self.time_frame) + "m", self.atr_period, self.short_period, self.long_period)
        
        self.new_command(Command(symbol, [self.atr_period, self.short_period, self.long_period, self.time_frame])) # atr, emashort, emalong, timeframe
        

    # To be called after all proper checks have been made
    def send_order(self, typ, symbol, vol, sl, tp):
        print("Sending order.")
        o1 = Command("buy", [symbol,vol, sl, tp])
        o2 = Command("buy", [symbol,vol, sl, 0])
        if typ != 0:
            o1 = Command("sell", [symbol, vol, sl, tp])
            o2 = Command("sell", [symbol, vol, sl, 0])
        
        self.new_command(o1)
        self.new_command(o2)
        s = "buy" if typ == 0 else "sell"
        print(symbol, s, "orders processing.")
        self.data.entry = None # reset entry
        
    
    # To be called when the user enters an order command
    def prime_order(self, side, symbol):
        market = self.data.market.search(symbol)
        if not market or not self.data.check_market(symbol): 
            self.fetch_market(symbol)
            print("Fetching data for market", symbol)
            return False
        
        print("Priming order for:", market.key)
        ask = market.search("ask")
        bid = market.search("bid")

        if side == 0:
            self.data.new_entry(side, ask, symbol)
        else:
            self.data.new_entry(side, bid, symbol)
        
        return True

    def is_buying(self):
        try:
            return self.data.entry.search("side") == 0
        except:
            return False
    
    def is_selling(self):
        try:
            return self.data.entry.search("side") == 1
        except:
            return False
    # To be called on update, call send_order if data allows
    def attempt_entry(self,symbol):
        side = -1 if not self.data.entry else self.data.entry.search("side")
        if side != -1: print("Analyzing current market conditions.")
        if not self.data.can_trade(symbol): return 0, side , symbol
        print("Trade check passed.")
        entry = self.data.entry
        symbol = symbol if symbol else entry.search("symbol") # If none is selected, assume that there is already a pending entry and grab its symbol
        side = entry.search("side")
        order = self.build_order(side, symbol)
        if side == 0:
            if True:
            #if self.data.can_buy(symbol): # Set to true for testing
                print("Buy confirmed.")
                self.send_order(side, order.symbol, order.vol, order.sl, order.tp)
                return self.info.find(order.symbol + " Entry#2 Attempt"), side, order.symbol
        elif side == 1:
            if True:
            #if self.data.can_sell(symbol): # Set to true for testin
                print("Sell confirmed.")
                self.send_order(side, order.symbol, order.vol, order.sl, order.tp)
                return self.info.find(order.symbol+ " Entry#2 Attempt"), side, order.symbol
        return 0, -1, symbol
    
    def calculate_lots(self, price, stop, market):
        """

        Helper function to calcuate the position size given a known amount of risk.

        *Args*
        - price: Float, the current price of the instrument
        - stop: Float, price level of the stop loss
        - risk: Float, the amount of the account equity to risk

        *Kwargs*
        - JPY_pair: Bool, whether the instrument being traded is part of a JPY
        pair. The muliplier used for calculations will be changed as a result.
        - Method: Int,
            - 0: Acc currency and counter currency are the same
            - 1: Acc currency is same as base currency
            - 2: Acc currency is neither same as base or counter currency
        - exchange_rate: Float, is the exchange rate between the account currency
        and the counter currency. Required for method 2.
        """

        if market.search("counter") == "JPY": #check if a YEN cross and change the multiplier
            multiplier = 0.00001
        else:
            multiplier = market.search("pip")

        #Calc how much to risk
        print("Calculating lots for", price, stop, abs(price - stop))
        print("Current Market:", market.key)
        account = self.data.account
        if not account:
            print("No account data loaded. Fetching...")
            self.new_command("account")
            return 0.01
        print("Account:", account)
        acc_value = account.search("free")
        cash_risk = acc_value * self.risk if self.risk < 1 else self.risk
        stop_pips_int = abs((price - stop) / multiplier)
        print("# of pips in stop dist:", stop_pips_int)
        pip_value = cash_risk / stop_pips_int
        print("calculated pip value:", pip_value)

        # Check acc currency to see which method is needed
        if account.search("currency") == market.search("counter"):
            method = 0
        elif market.search("base") == account.search("currency"):
            method = 1
        else:
            method = 2

        if method == 1:
            pip_value = pip_value * price
            units = pip_value / 2
            print("Lots calculated:", units)
            
        elif method == 2:
            pip_value = pip_value * market.search("rate")
            units = pip_value / 2
            print("Lots calculated:", units)

        else: # is method 0
            units = pip_value / 2
            print("Lots calculated:", units)
        
        print(units, " Calculated.")
        
        return flat_float(units, 2)

    def save_logs(self):
        if self.info.has() :
            self.info.compile()
        if self.errors.has() :
            self.errors.compile()
        if self.analysis.has() :
            self.analysis.compile()