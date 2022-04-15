
from collections import namedtuple

Symbol = namedtuple('Market', 'symbol ask bid periods opens closes highs lows longmeans shortmeans volumes atrs') #note periods is an array [ time_frame, longperiod, shortperiod ]
Acc = namedtuple('Account', 'name margin_avail acc_curr profit')
Rate = namedtuple('Rate', 'symbol rate') # symbol is the pair where exchange is needed so GBP/JPY is symbol, rate would be USDJPY

class Market:
    # Contains all relevant market data for the past bars
    # Note the data is constructed for any time frame
    """
        time % 120 = use 2hr + 2hr... to form candle
        time % 60 = 0, use 1hr + 1hr to form candle
        time % 30 = 0, use 30 min
        time % 15 etc

        ! short/long means will have to be built by ema of bar + bar + bar / # for an avg mean over the period ! 
            ^ This leads to miscalculation, better to calculate the EMA and ATR on the back end after gathering hloc data


    """
    def __init__(self, data):
        # data is constructed as such symbol:timeframe:ask:bid:totalbars:opens[]:closes[]:highs[]:lows[]:longmeans[]:shortmeans[]:volumes[]:atrs[]

        self.markets = []
     
        for m in data:
            
            market = Symbol(m.name, m.ask, m.bid, m.currency_base, m.currency_profit, m.point, rate)
            self.markets.append(market)

    def get_market(self, symb):

        for m in self.markets:
            if m.name == symb:
                return m

        return None
        
class Account:
    def __init__(self, data):
        # margin_free, currency, name, profit
        self.acc = Acc(data.name, data.margin_free, data.currency, data.profit)
        

        



def config():
    return True