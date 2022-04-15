
class Candle:
    def __init__(self, data):
        self.time = data[0]
        self.open = data[1]
        self.high = data[2]
        self.low = data[3]
        self.close = data[4]
        self.volume = data[5]

class Market:
    def __init__(self,symbol, data):
        self.candles = []
        self.symbol = symbol
        # Turn the data into nice values
        for d in data:
            self.candles.append(Candle(d))
        first = self.candles[0]
        second = self.candles[1]

        self.close = first.close
        self.open = first.open
        self.low = first.low
        self.high = first.high
        self.last_close = second.close
        self.last_open = second.open
        self.last_low = second.low
        self.last_high = second.high
