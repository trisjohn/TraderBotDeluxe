
import datetime

class Account:
    def __init__(self):
        self.free = 0
        self.currency = "USD"
        self.canTrade = True
        self.server_time = 0
        self.local_time = datetime.datetime.now()
        self.profit = 0
        self.positions = []
        self.exposure = 0.0 # For all open position => pos1 risk + sum(posx risk * correlation)
        self.exposure_limit = -.05 # Percentage of equity drop that bars new orders from being entered