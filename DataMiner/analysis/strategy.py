import pandas as pd
import numpy as np

"""
    TO DO:
    Add a way to collect more data per trade (for later optimizations)
"""

class TestEntry:
    """
    Build and track a fake order.
    Give a side, entry price, cost in $, spread value, target_price, stop_price
    Call update each iteration, given new candle data and or exit boolean
    """
    def __init__(self,id, side, price, cash_val, spread, target=0, stop=0):
        self.id = id
        self.side = side
        self.target = target
        self.stop = stop
        self.track_distance = self.target == 0
        self.open = price - spread if side == 1 else price + spread
        self.cost = cash_val
        self.profit = cash_val * abs(target - self.open) / abs(stop - self.open)
        print(id, end=">")
    
    def update(self, ohlc, exit_trade=False):
        """
        Update order. Check ohlc is stop or target hit or if exit is true.
        if exit is true, return val (close - distance) / stop * cash
        """

        if self.side == 0:

            if exit_trade:
                return (ohlc['close'] - self.open) / (self.open - self.stop) * self.cost

            # Buy rules
            if ohlc['high'] >= self.target:
                # print(self.id,"Buy Target hit +$", self.profit)
                if not self.track_distance:
                    return self.profit
            elif ohlc['low'] <= self.stop:
                # print(f"{self.id} Sell Stop Loss hit -${self.cost}")
                return self.cost
        else:
            if exit_trade:
                return (self.open - ohlc['close'] ) / (self.open - self.stop) * self.cost
            # Sell rules
            if ohlc['high'] >= self.stop:
                # print(f"{self.id} Sell Stop Loss hit -${self.cost}")
                if not self.track_distance:
                    return self.cost
            elif ohlc['low'] <= self.stop:
                # print(self.id,"Sell Target hit +$", self.profit)
                return self.profit
        return 0

# RunStrategy Takes in a pandas dataframe with atleast OHLC data. Other columns must be of the correct name and formatted correctly:
#   'long ema', 'short ema', 'atr'
class RunStrategy:
    """
    Takes in a pandas dataframe with atleast OHLC data. Other columns must be of the correct name and formatted correctly:
        'long ema', 'short ema', 'atr'
    Give a number of bars to test strategy (0 is all)
    Give an entry rule: ['ema cross', 'ema reject']
    Give a confirmation rule ['long ema', 'greater volume', 'last close', 'last low', 'last high']
        Where price must be above/below for buy sell/respectively.
    Give a target distance in mult of atr ( 0 means track max pos distance until next entry)
    Give a loss distance in mult of atr ( 0 means track max neg distance until next entry)
    Allow Multiple Trades = False (Allow multiple trades to be open at once) If left False, sell orders will close buy orders and vice versa.

    Starts with a balance of 10000 and risks 1% per trade. Uses 0.25% of trade as commission, and uses rand(10,20)% atr as spread.
    """
    def __init__(
        self, data, length=0, 
        entry_rules=['ema cross', 'ema reject'],
        con_rules=['long ema', 'greater volume', 'last close', 'last low', 'last high'],
        target=0, stop=0, allow_multiple_trades=False,
        start_bal = 1000, risk = 15, commission = 0.035
    ):
        self.data = data
        self.length = length
        self.e_rules = entry_rules
        self.c_rules = con_rules
        self.target = target
        self.stop = stop
        self.start_date = data.index[0]
        self.end_date = data.index[length-1]
        self.counts = (0,0) # Wins, Losses
        self.order_num = 0
        self.many_trades = allow_multiple_trades
        self.start_balance = start_bal
        self.balance = start_bal
        self.risk = risk
        self.static_risk = risk > 1
        self.comission_per_trade = commission
        self.entries = []
        results = self.run_report()
        self.stats = None
        if results[0] == 0 and results[1] == 0: raise Exception("No Results recorded!", results)
        else: print(f"Simulation completed with {self.order_num} total orders placed.")
        self.show_stats(results)

    def show_stats(self, results):

        w, l, draw, end = results
        total = w + l
        win_rate = round(w / total * 100)
        loss_rate = round(l / total * 100)
        roi = round(self.balance / self.start_balance * 100)
        df = pd.DataFrame(
            [end, int(total), int(w), int(l), draw * 100, win_rate, loss_rate, roi, self.start_date, self.end_date], 
            ['total profit', 'total trades', 'wins', 'losses', 'max drawdown', 'win rate', 'loss rate', 'ROI', 'start date', 'end date']
        )
        print(df)
        self.stats = df

    
    def pass_entry_rules(self, side, last, curr):
        """
        Check if the market conditions are appropriate given the strategy's entry rules for an entry of the given side
        """
        if side == 0:
            for e in self.e_rules:
                open = curr['open']
                close = curr['close']
                mean = curr['short ema']
                if e == 'ema cross':
                    buy = close > mean and open < mean
                    if buy: return True
                if e == 'ema reject':
                    buy = curr['low'] <= mean and close > mean
                    if buy: return True
        elif side == 1:
            for e in self.e_rules:
                open = curr['open']
                close = curr['close']
                mean = curr['short ema']
                if e == 'ema cross':
                    sell = close < mean and open > mean
                    if sell: return True
                if e == 'ema reject':
                    sell = curr['high'] >= mean and close < mean
                    if sell: return True
        
        return False

    def pass_con_rules(self, side, last, curr):
        """
        Check the confirmations for each side, position passes only if it matches the specified number of criterium
        """
        close = curr['close']

        if side == 0:
            for r in self.c_rules:
                if r == 'long ema' and close < curr['long ema']: return False
                elif r == 'greater volume' and curr['volume'] < last['volume']: return False
                elif r == 'last close' and close < last['close']: return False
                elif r == 'last low' and close < last['low']: return False
                elif r == 'last high' and close < last['high']: return False
        else:
            for r in self.c_rules:
                if r == 'long ema' and close > curr['long ema']: return False
                elif r == 'greater volume' and curr['volume'] < last['volume']: return False
                elif r == 'last close' and close > last['close']: return False
                elif r == 'last low' and close > last['low']: return False
                elif r == 'last high' and close > last['high']: return False
        # print(f"Confirmation rules passed. {'buy' if side == 0 else 'sell'}")
        return True



    def check_entry(self, last_data, curr_data):
        """
        Given the last candle and current candle, see if an entry is to be made.
        """ 

        is_buy = self.pass_entry_rules(0, last_data, curr_data) and self.pass_con_rules(0,last_data, curr_data)
        is_sell = self.pass_entry_rules(1,last_data, curr_data) and self.pass_con_rules(1,last_data, curr_data)

        if not is_buy and not is_sell: return None
        side = 0 if is_buy else 1
        self.order_num += 1
        price = curr_data['close']
        atr = curr_data['atr']
        target = price + self.target * atr if side == 0 else price - self.target * atr
        stop = price - self.stop * atr if side == 0 else price + self.stop * atr
        if(self.balance <= 0): raise Exception("Strategy failed after", self.order_num)
        risk = self.balance * self.risk if not self.static_risk else self.risk
        return TestEntry(
                self.order_num,side,price,
                risk,np.random.randint(10,20) / 100 * atr,
                target,stop
                )
        

    def run_report(self):
        """
        Simulate the strategy on the data, following the given entry and target rules
        Return the wins, losses, max drawdown
        """
        total = self.length if self.length > 0 else len(self.data)
        max_draw = 0 # max % negative the balance goes 
        max_balance = self.balance # highest recorded balance

        for i in range(1, total):
            if i >= total:
                print(f"Test completed of {self.o_count} orders")

            curr_candle = self.data.iloc[i]
            entry = self.check_entry(self.data.iloc[i-1], curr_candle)
            if entry:
                self.entries.append(entry)
                if not self.many_trades: close_trade = self.entries[0].side != entry.side
            for position in self.entries:
                change = position.update(curr_candle, close_trade)
                w, l = self.counts
                if change == 0: continue
                else: self.entries.remove(position)
                if change < 0:
                    l += 1
                else:
                    w += 1
                self.counts = (w, l)
                self.balance += change - (position.cost * self.comission_per_trade)
                if self.balance > max_balance: max_balance = self.balance
                current_draw = (max_balance - self.balance) / max_balance
                if current_draw > max_draw : max_draw = current_draw
        return (self.counts[0], self.counts[1], max_draw, self.balance)
                
            

    