
from lib.position import Position
from lib.logger import *

class PositionManager:
    """
        [ Position Manager
            Positions are checked using their open time and ticket values
            When Target (maxpositive > takedist) is reached, 1. close the ticket that has a tp value
            2. Position stop updated to break even, 3. Position trail follows current low/high by traildist,
            4. Positions close command if market close passes exit, or ask/bid crosses stop or trail.
            5. Position closes if < 5 min before major news on Base or Counter currency of position pair
        ]
    """
    def __init__(self, args):
        """ Dictionary has: take dist, stop dist, even dist, trail dist, close on line

        """
        self.positions = [] # all the current open positions
        self.vars = args
        self.info = [] ### Append all loggables


    def check_open(self, data):
        """
            Note: to be called after creating any new position objects
            Takes the tickets of current positions and matches them to existing.
            Returns the positions that existed in the Position Manager that did not exist in the incoming data
            AKA the closed positions' tickets
            
            Data should be an array with:
            [tickets]

            return is an array of:
            [(symbol, tickets, bar time - open time)]
            open time is the time of the bar position was opened on
        """
        closed = []
        for p in self.positions:
            found = False
            for d in data:
                if p.tickets == d: found = True
            if not found : closed.append(p.tickets)
                
        return closed

    
    def fill_closed(self, data):
        """
            After checking open, reach out to server for data of the following structure:
            [(tickets, close time, profit)] ### LATER ADD MAX NEG and MAX POS as well as PRE candles
        """
        if not data or len(data) < 1: 
            print("No closed positions detected.")
            return
        for d in data:
            tickets, ctime, profit = d
            for p in self.positions:
                if p.tickets == tickets:
                    p.close_and_save({"close time": ctime, "final profit": profit})


    def update_open(self, data_arr):
        """
            data_arr contains a dictionary of each of the current open positions data:
            [ {tickets: [], open_prices = [], symbol = ", side = #, profit: #, ask: #, bid: #, 
                low: #, high: #, last close: #, mean=#, open time=(time of bar of position open),
                volume: (lots), atr: (atr at bar of position open)} ]
            creates new position if position manager doesnt have
        """
        for d in data_arr:
            found = False
            for p in self.positions:
                if p.tickets != d['tickets'] and not d['tickets'][0] in p.tickets: continue
                print(f"Position found, updating {'buy' if d['side'] == 0 else 'sell'} on {d['symbol']}")
                dict = {
                    'tickets' : d['tickets'] if len(d['tickets']) > 1 else d['tickets'] + [-1],
                    'profit': d['profit'],
                    'ask' : d['ask'],
                    'bid': d['bid'],
                    'low': d['low'],
                    'high': d['high'],
                    'last close':d['last close'],
                    'mean': d['mean']
                }
                p.update(dict, self.vars)
            if not found:
                print(f"New Position entered on {d['symbol']}, {'buy' if d['side'] == 0 else 'sell'} of {d['volume']}")

                o1, o2 = d['open_prices']
                avg_price = (o1 + o2) / 2
                self.positions.append(
                    Position(
                        d['side'], d['symbol'], d['tickets'], d['open time'], avg_price, d['volume'], d['atr']
                    )
                )

