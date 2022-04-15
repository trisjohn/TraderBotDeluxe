
from lib import thread
import time
from mistertrack5.meta import *
from mistertrack5.market import *

class Position:
    def __init__(self, data):
        o = 0
        p = 0
        t = []
        lots = []
        for d in data:
            o += d.open_price
            p += d.profit
            t.append(d.ticket)
            lots.append(d.volume)
        self.tickets = t
        self.lots = lots
        self.side = d[0].type
        self.open_price = o / len(data)
        self.open_time = data[0].time
        self.close_time = 0
        self.close_price = 0
        self.symbol = data[0].symbol
        self.profit = p
        self.data = [] # holds whatever data to save for positions (numpy array)
    
    def gather(self, n):
        # Gathers n amount of data to be saved
        self.data = get_data(self.symbol,n)
        # Save all data (pandas)
        # Searches current file for existing position data and overwrites if found

def get_position(symbol):
    # gather and build position
    return Position(Meta().position(symbol))

# Pass in symbol of open position to Counter close on
class BeginCounterClose:
    # Close at next negative bar close [ buy: close < open, high < lasthigh, sell: close > open, low > lastlow ]
    def close_loop(self):
        for i in count():
            market = None
            if i % 30 == 0: 
                print("Counter-closing on", self.symbol)
                market = Market(self.symbol, get_data(self.symbol,2))
            if market:
                if (self.position.side == 0 and market.close < market.open and market.high < market.last_high) or \
                    (self.position.side == 1 and market.close > market.open and market.low > market.last_low):
                    Meta().close_position(self.position)

            time.sleep(1)


    def __init__(self, args):
        self.symbol = args
        self.position = get_position(args)
        thread.side_thread(20, "Counter Close"+args,self.close_loop)

class BeginPositionEntry:

    def open_loop(self):
        n = self.number
        for i in count():
            successes = Meta().enter_new_position(self.request, n)
            if successes == n or n == 0:
                n -= successes
                print("Position entry succeeded.")
                break
            else:
                print("Position not fully entered. Remaining", n, "of", c)

    def __init__(self, side, args, number=2):
        t = mt5.ORDER_TYPE_BUY_LIMIT if side == 0 else mt5.ORDER_TYPE_SELL_LIMIT

        # Sended all necessary symbol info
        info = Meta().get_market(args)

        price = info.bid if side == 1 else info.ask
        atr = get_atr(args, ATR_PERIOD)

        stop = STOP_LOSS * atr 
        take = TAKE_PROFIT * atr
        stop = stop if stop > info.minstop * info.point else info.minstop * info.point
        stop = price - stop if side == 0 else price + stop
        take = price - stop if side == 0 else price + stop
        self.number = number
        lots = Meta().calculate_lots(abs(stop - price), info, number) # dist, info, # of trades
        self.request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": args,
            "volume": lots,
            "type": t,
            "price": price,
            "sl": stop,
            "tp": take,
            "deviation": 10,
            "magic": 0,
            "comment": "python script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        thread.side_thread(21, "Open"+str(side)+" "+args,self.open_loop)

class BeginLineEntry:
    def open_loop(self):
        n = self.number
        for i in count():
            if Meta()
            successes = Meta().enter_new_position(self.request, n)
            if successes == n or n == 0:
                n -= successes
                print("Position entry succeeded.")
                break
            else:
                print("Position not fully entered. Remaining", n, "of", c)

    def __init__(self, side, symb, a, b, number=2):
        self.number = number
        self.side = side
        self.symbol = symb
        if side == 0:
            # Reach to grab the highs at the specific times
            # Build a line using the data where (a, highA), (b, highB)
            self.line = None
        else:
            # Grab the lows at the specific times
            # Build a line using the data where (a, lowA), (b,lowB)
            self.line = None
        thread.side_thread(22, "Line Open"+str(self.side)+" "+symb, self.open_loop)