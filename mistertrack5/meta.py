from mistertrack5.logger import *
from datetime import datetime, timedelta
from itertools import count
import time
import pandas as pdimport
import MetaTrader5 as mt5


### USER SETTINGS

# Stop loss (mult of atr)
STOP_LOSS = 1
RISK = .02
# Take profit (mult of atr)
TAKE_PROFIT = 1.5
BREAK_EVEN = 0.3
ATR_PERIOD = 20
# Replace in line 113 to choose between a BUY or SELL order
BUY = mt5.ORDER_TYPE_BUY
SELL = mt5.ORDER_TYPE_SELL

class Meta:

    def authorize(self, acc):
        authorized = mt5.login(acc)
        if authorized:
            print(f'connected to account #{acc}')
        else:
            e = mt5.last_error()
            log_error("failed to connect to account", e)
            print(f'failed to connect at account #{acc}, error code: {e}')
        return authorized
    
    def account_info(self):
        # store the equity of your account
        info = mt5.account_info()
        if info is None:
            raise RuntimeError('Could not load the account equity level.')
        else: 
            ### formata data for account
            clean = info
            print(clean)
            return clean

    def calculate_lots(self, dist, market, n):
        pips = dist / market.point
        acc = self.account_info()
        cash = acc.margin_free * RISK
        risk_pips = cash /pips
        if market.currency_base == acc.currency:
            lots = risk_pips/(10**(acc.currency_digits-1)) # / CurrencyRates().get_rate(acc.currency, market.currency_profit)
        elif market.currency_profit == acc.currency:
            lots = risk_pips/(10**(acc.currency_digits-1))
        else:
            lots = risk_pips/(10**(acc.currency_digits-1)) # / CurrencyRates().get_rate(market.currency_profit, acc.currency_profit)
        
        return lots

    def last_close(self, symbol, tf =15):
        now = datetime(mt5.symbol_info_tick(symbol).time)
        back = now - timedelta(minutes=15)
        return mt5.copy_rates_from(symbol, back, now).close

    def get_market(self, symbol):
        info = mt5.symbol_info(symbol)

        if info is None:
            print(f'{symbol} not found, critical error')
            log_error("Symbol info not found", mt5.last_error())
            mt5.shutdown()
            # if the symbol is unavailable in MarketWatch, add it
        if not info.visible:
            print(f'{symbol} is not visible, trying to switch on')
            if not mt5.symbol_select(symbol, True):
                log_error("Symbol select failed (not visible)", mt5.last_error())
                print('symbol_select({}}) failed, exit', symbol)

        print(info)
        return info
    
    def position(self,symbol):
        position = mt5.positions_get(symbol)
        print(position)
        return position

    def __init__(self):
        # connect to the trade account without specifying a password and a server
        mt5.initialize()
        # account number in the top left corner of the MT5 terminal window
        # the terminal database password is applied if connection data is set to be remembered
        account_number = 1080192
        self.authorized = self.authorize(account_number)
        self.account = self.account_info()
    
    def enter_new_position(self, req, number):
        """ enter a new position given the request and the number of times to repeat the request. Return the number of requests successfully completed."""
        tickets = []
        for x in range(number):
            result = mt5.order_send(req)
            print(result)
            s = req.symbol + req.side + " of " + req.volume + "@" + req.price +" s=" + req.sl + " t=" + req.tl
            if result.retcode > 0:
                print("Error sending request.")
                log_error("Failed Entry: "+s, result.retcode)
            else:
                print("order successfully entered", result.order, result.deal, result.price)
                log("Position entered: "+s, result.order)
                tickets.append(result.order)
        
        return len(tickets)


    def close_position(self, pos):
        bid, ask = get_bid_ask(pos.symbol)
        price = bid if pos.side == mt5.ORDER_TYPE_BUY else ask
        for t in pos.tickets:
            
            close_request={
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": pos.side,
                "position": t,
                "price": price,
                "deviation": 7,
                "magic": 0,
                "comment": "TBD-mt5 close",
                "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            # send a trading request
            result = mt5.order_send(close_request)
            print(result)


def get_dates(symbol, bars_back, tf = 15):
    """Use dates to define the range of our dataset in the `get_data()`."""
    now = datetime(mt5.symbol_info_tick(symbol).time)
    just_closed = now.minute % tf == 0
    utc_from = now - timedelta(minutes = tf * bars_back)
    return utc_from, now, just_closed


def get_data(symbol, n):
    """Download an n amount of candles."""
    utc_from, utc_to, just_closed = get_dates(symbol, n)
    if just_closed:
        return mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, utc_from, utc_to)
    else:
        None

### CALCULATIONS

def wwma(values, n):
    """
     J. Welles Wilder's EMA 
    """
    return values.ewm(alpha=1/n, adjust=False).mean()

def get_atr(symbol, period):
    """Download candles and calculate atr"""
    utc_from, utc_to, _ = get_dates(symbol, period+1)
    data = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, utc_from, utc_to)
    data_frame = pd.DataFrame(data)
    high = data_frame['high']
    low = data_frame['low']
    close = data_frame['close']
    data_frame['tr0'] = abs(high - low)
    data_frame['tr1'] = abs(high - close.shift())
    data_frame['tr2'] = abs(low - close.shift())
    tr = data_frame[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = wwma(tr, period)
    return atr

def get_bid_ask(symbol):
    """Return current bid and ask."""
    a = mt5.symbol_info_tick(symbol)[2]
    b = mt5.symbol_info_tick(symbol)[1]
    return b, a


def trade():
    """Determine if we should trade and if so, send requests to MT5."""
    pass


# if __name__ == '__main__':
#     print('Press Ctrl-C to stop.')
#     for i in count():
#         trade()
#         print(f'Iteration {i}')
#         time.sleep(5)