

# Given a float and a number of digits, cut off the float keeping the number of specified digits
from collections import namedtuple


def flat_float(f, x):
    big = f * (10 ** x)
    return round(big) / (10 ** x)

PositionManager = namedtuple('PositionManager', 'symbol side break_even trail_stop is_exit')

class Dictionary:

    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def __str__(self):
        s = ""
        if self.val_is_array() and len(self.value) > 0:

            s = "".join([str(item) for item in self.value])
        else:

            s = str(self.value) if self.value else ""

        return "<"+self.key + " " + s+">"

    def __iter__(self):
        pass
        
    def update(self, key, new_val):

        if key == self.key:
            self = new_val
            return True

        if self.val_is_array():
            for dic in self.value:
                if dic.key == key: 
                    if isinstance(new_val, Dictionary):
                        if new_val.val_is_array():
                            dic = new_val
                        elif new_val.value != dic.value:
                            dic = new_val
                    elif new_val != dic.value:
                        dic.value = new_val
                    return True
                    

        if self.val_is_dict() and self.key == key and self.value != new_val:
            self.value = new_val
            return True

        return False  
    
    # check if self.val is array
    def val_is_array(self):
        return isinstance(self.value, list)
    
    def size(self):
        if not self.val_is_array() : return 1
        return len(self.value)

    # Only usable if is an array
    def add(self,val):
        if not self.val_is_array() : return
        self.value.append(val)
    
    def delete(self,k):
        if self.val_is_array():
            for dict in self.value:
                if dict.key == k: 
                    self.value.remove(dict)
                    return
        if self.val_is_dict() and self.key == k:
            self = None 
        else:
            print(self.key," is unable to find key of dictionary to delete:", k)

    def val_is_dict(self):
        return isinstance(self.value, Dictionary)

    def search(self, key):
        if self.val_is_array():
            for dict in self.value:
                if dict.key == key: 
                    return dict.get()
        if self.val_is_dict() and self.key == key:
            return self  
        
        return None
    # Return true if last in tree
    def get(self):
        if not self.val_is_array():
            return self.value
        return self

# Data holds all relevant data, but needs to be told when and what to update.
# EX. If checking for a buy (to send order), one must send for the relevant market data, update_market and then call check_buy
class Data:
    def __init__(self, take, stop, risk):
        # Hold all market info for each symbol : Ask, Bid, pip, digits, high, low, close, lasthigh, lastlow, lastclose
        # emalong, emashort, atr, base, counter, rate, barready
        self.market = Dictionary("symbols", [])
        # Holds all acc data : currency,free,equity,profit
        self.account = None # key-value pair
        # Holds all positions data : 'symbol',ticket1,ticket2,open,lots,sl,tp,profit, side
        self.positions = Dictionary("positions", []) #keys are symbols
        # Holds info for a potential entry : side, price
        self.entry = None
        self.take = take
        self.stop = stop
        self.risk = risk
        self.target = 500
        self.recentlyEntered = False # Set true/false by outside timer

    # return true if market is holding data for atleast one symbol
    def has_market(self, symbol=None):
        # print("Checking market", len(self.market.value))
        if symbol == None:
            return self.market.val_is_array() and len(self.market.value) > 0
        else:
            return self.market.search(symbol) != None

    # check for existing symbol and update, if not there, create a new one
    def update_market(self, data):
        # DATA IS NOW A DICTIONARY OF ALL SYMBOLS REQUESTED, UPDATE/CREATE ACCORDINGLY
        keys = ["ask", "bid", "pip", "digits", "high", "low", "close", "lasthigh", "lastlow", "lastclose", 
                "emalong", "emashort", "atr", "base", "counter", "rate", "maxlot", "barready", "minstop"]
        for d in data.value:
            symbol = self.market.search(d.key)
            print("Existing Symbol?", symbol)
        
            if not symbol:
                symbol = Dictionary(d.key, [])
                for k, v in zip(keys, d.value):
                    symbol.add(Dictionary(k, v))
                self.market.add(symbol)
                print("Symbol created:", symbol.key)
            else:
                for k, v in zip(keys, d.value):
                    existing = symbol.search(k)
                    if not existing and existing != 0:
                        print("Key missing on symbol, adding", k, v)
                        symbol.add(Dictionary(k,v))
                    elif k == "barready" and v == 1:
                        print("bar is ready!")
                        if not symbol.update(k,v):
                            raise Exception("Critical failure when updating symbol's barready status", symbol, k, v)
                    elif symbol.update(k,v):
                        print(".",end="")
                        # print("Updating", k, symbol.search(k), "=",v)
                print("\nSymbol updated:", symbol.key)
                self.market.update(d.key, symbol)
    
            print(d.key, "market built.", len(self.market.search(d.key).value), "items total.")
    
    # Cycle through position and check + return Symbol{break even, trail stop, isExit}
    def manage_positions(self, break_even_dist, trail_dist):
        b = 0
        t = 0
        c = False
        arr = []

        print("Open positions = True") if len(self.positions.get().value) > 0 else print("No positions.", self.positions.get())
        
        for p in self.positions.get().value :
            sym = p.key
            if len(sym) != 6 : continue
            if not self.check_market(sym): arr.append(sym) # Return the symbol if market doesnt exist
            print("Managing positions for", sym)
            b = self.break_even(p, break_even_dist)
            t = self.trail_stop(p, trail_dist)
            c = self.exit_signal(p)
            arr.append(PositionManager(sym, p.search("side"),b,t,c))
        return arr

    def stop_triggered(self, symbol, side, price):
        market = self.market.search(symbol)
        return market.search("ask") < price  if side == 0 else market.search("bid") > price
        
    # Returns true if all necessary values are non-zero, false otherwise.
    def check_market(self, symbol):
        market = self.market.search(symbol)
        if not market:
            print(symbol, "Market not found.") 
            return False
        for d in market.value:
            if isinstance(d.value, float) and d.value == 0 and d.key != "barready": 
                print("Missing data found on",symbol, d)
                return False
        print(symbol, "Market data is valid.")
        return True

    def update_account(self, data):
        data.pop(0)
        print("Building account data.", data)
        keys = ["currency","free", "equity", "profit"]
        self.account = Dictionary("account", [])
        for k, v in zip(keys, data):
            if k == "free":
                self.target = (self.take/self.stop)*(self.risk * v) if self.risk < 1 else (self.take/self.stop)*self.risk
            self.account.add(Dictionary(k,v))

    def update_positions(self, data, take_dist):
        keys = ["ticket1","ticket2","open","lots","sl","tp", "profit", "side"]
        # store the symbols of those positions that were updated, if there is a position on server side that is not on client side, remove it.
        updated = []
        self.take = take_dist
        for d in data:
            try:
                name = d[0]
            except: 
                print("Position data corrupted or incomplete.")
                return
            d.pop(0)
            symbol = self.positions.search(name)
            updated.append(name)
            if not symbol:
                symbol = Dictionary(name, [])
                # print("Building new position", symbol)
                for k, v in zip(keys, d):
                    symbol.add(Dictionary(k,v))
                    # print(symbol, k, v)
                # add max profit
                symbol.add(Dictionary("maxprofit", symbol.search("profit")))
                self.positions.add(symbol)
                print("Position added.", symbol)      
            else:
                #print("Position Symbol data found.", symbol)
                # print("Current positions", self.positions)
                for k, v in zip(keys, d):
                    val = symbol.search(k)
                    if not val and k != "sl" and k != "tp" and k != "side":
                        print("Position missing data", k, v)
                        symbol.add(Dictionary(k,v))
                    symbol.update(k, v)
                    if k == "profit" and v > symbol.search("maxprofit"):
                        symbol.update("maxprofit", v)
                self.positions.update(name, symbol)
                print("Position updated.", symbol)

        for p in self.positions.value:
            found = False
            for u in updated:
                if p.key == u:
                    found = True
            if not found:
                self.positions.value.remove(p)

    def can_trade(self, symbol):
        if not self.entry_valid():
            print("No valid entry")
            return False
        if not self.bar_ready():
            print("Bar is not recently closed")
            return False
        if self.recentlyEntered:
            print("Recently entered trade")
            return False
        if not self.entry.search("symbol") == symbol:
            print("Entry symbol doesn't match", symbol)
            return False
        return True

    # Return position, market data if it exists
    def market_data(self, symbol):
        data = self.positions.search(symbol)
        market = self.market.search(symbol)
        return data, market

    # Given a symbol, check if target has been reached or not    
    def target_hit(self, symbol):
        
        data, market = self.market_data(symbol)
        if not data or not market : return False
        # print("Positon found, analyzing...", data.key, data.value)
        # print("Market found, analyzing...", market)
        return data.search("maxprofit") >= self.target if self.target > 50 else self.account.search("free") 
    
    # Return true if bar recently closed, check this before certain actions
    def bar_ready(self):
        if len(self.market.value) < 1:
            print("No market data loaded!")
            return False
        if self.entry_valid():
            return self.market.search(self.entry.search("symbol")).search("barready") == 1
        else:
            return self.market.value[0].search("barready") == 1
    
    # return break even value for a position on the given symbol, return 0 if no applicable break even
    def break_even(self, data, size):

        _, market = self.market_data(data.key)
        if not data or not market or not self.target_hit(data.key) : return 0

        side = data.search("side")
        open = data.search("open")
        atr = market.search("atr")
        stop = data.search("sl")
        digs = market.search("digits")
        if side == 0 and open + size * atr > stop:
            print("Buy break even triggered.")
            return flat_float(open + size * atr, digs)
        elif side == 1 and open - size * atr < stop:
            print("Sell break even triggered.")
            return flat_float(open - size * atr, digs)
        print("Break even qualifications not met.")    
        return 0

    # Return value of the trailing stop for a position on the given symbol, return 0 if no applicable trail
    def trail_stop(self, data, size):

        _, market = self.market_data(data.key)
        if not data or not market or not self.bar_ready() or not self.target_hit(data.key): return 0
        print("Looking for trail stop value for", data.key)
        side = data.search("side")
        anchor = market.search("low") if side == 0 else market.search("high")
        atr = market.search("atr")
        stop = data.search("sl")
        digs = market.search("digits")
        print(data.key, anchor, atr, stop, digs)
        if side == 0 and anchor - size * atr > stop:
            anchor = anchor - size * atr
        elif side == 1 and anchor + size * atr < stop:
            anchor = anchor + size * atr
        else:
            anchor = 0
        print("Trail stop =", anchor)
        return flat_float(anchor, digs)
    
    # Given a symbol, determine if a position should be exited (cross over emashort) or not
    def exit_signal(self, data):
        _, market = self.market_data(data.key)
        if not data or not market or not self.bar_ready() or not self.target_hit(data.key): return False

        side = data.search("side")
        ema = market.search("emashort")
        anchor = market.search("low") if side == 0 else market.search("high") 
        close = market.search("close")
        return self.target_hit(data.key) and ( (side == 1 and anchor <= ema and close > ema) or (side == 0 and anchor >= ema and close < ema) )

    # check if entry is valid still
    def entry_valid(self):
        return self.entry != None

    # check if price is still in entry zone, if not, remove entry price ("side", "price")
    def in_zone(self, symbol):
        market = self.market.search(symbol)
        if not market or not self.entry : return False
        side = self.entry.search("side")
        current = market.search("ask") if side == 0 else market.search("bid")
        anchor = self.entry.search("price")

        b = abs(current - anchor) <= market.search("atr")
        if not b:
            print("Price (",current,") out of zone", anchor)
            self.entry = None
        
        return b

    def new_entry(self, side, price, symbol):
        self.entry = Dictionary("entry", [])
        self.entry.add(Dictionary("side", side))
        self.entry.add(Dictionary("price", price))
        self.entry.add(Dictionary("symbol", symbol))
        print("New Entry Created", self.entry)

    # check if can sell
    def can_sell(self, symbol):
        market = self.market.search(symbol)
        if not market : return False
        bid = market.search("bid")
        # check if an entry has already been started or not, if it exists and its the opposite side, change it
        if not self.entry or self.entry.search("side") == 0:
            self.new_entry(1, bid, symbol)
        close = market.search("close")
        lastclose = market.search("lastclose")
        high = market.search("high")
        lasthigh = market.search("lasthigh")
        lastlow = market.search("lastlow")
        print("Analyizing market conditions for sell")
        yes = self.in_zone(symbol) and self.bar_ready() and (high < lasthigh or close < lastlow)
        # close is lower than last close or not
        print("=>", close < lastclose)
        if close > lastclose : return False
        # high is lower than last high or close is lower than last low
        print("=>", yes)
        return yes

    # check if can buy
    def can_buy(self, symbol):
        market = self.market.search(symbol)
        if not market : return False
        ask = market.search("ask")
        # check if an entry has already been started or not, if it exists and its the opposite side, change it
        if not self.entry or self.entry.search("side") == 1:
            self.new_entry(1, ask, symbol)
        close = market.search("close")
        lastclose = market.search("lastclose")
        low = market.search("low")
        lasthigh = market.search("lasthigh")
        lastlow = market.search("lastlow")
        yes = self.in_zone(symbol) and self.bar_ready() and (low > lastlow or close > lasthigh)
        print("Analyzing market conditions for buy")
        print("=>", close > lastclose)
        # close is higher than last close
        if close < lastclose : return False
        # low is higher than last low or close is higher than last high
        print("=>", yes)
        return yes
    
    # return stops
    def get_stops(self, symbol, side, stop_dist, take_dist):
        market = self.market.search(symbol)
        if not market: return 0,0
        price = market.search("ask") if side == 1 else market.search("bid")
        atr = market.search("atr")
        take_val = take_dist * atr if take_dist * atr > market.search("minstop") else market.search("minstop") + 0.1 * atr
        stop_val = stop_dist * atr if stop_dist * atr > market.search("minstop") else market.search("minstop") + 0.1 * atr
        stop = price + stop_val
        take = price - take_val
        digits = market.search("digits")
        if side == 0 :
            stop = price - stop_val
            take = price + take_val
        print("Calculated stops for order @", price, stop, take)
        return flat_float(stop, digits), flat_float(take, digits)
