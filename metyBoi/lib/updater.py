from datetime import date, datetime
from lib.positionmanager import *
from lib.connection import *
import datetime
import time

class Updater:
    """ Runs on a timer, reading trade file > watching for new trades > deleted expired or filled trades
        Pulling json data from server, sending json data to server 
        Watches over positions
        Records info for logging, saves position and market data pertaining to each position
        Dependecies: Position, PositionManager     
    """
    def timer(self, dt):
        self.update()
        curr = datetime.datetime.now()
        if curr - datetime.timedelta(seconds=1) >= dt:
            if self.alive: self.timer(curr)
        else:
            time.sleep(1)
            if self.alive: self.timer(curr)
        print("Update timer finished.")

    def __init__(self, client, path):
        """ Needs a client (connection to MT4 MB Client) and a path to the saves directory.
            Will pull necessary info like market technicals and order management vars
        """
        self.client = client
        self.alive = True
        self.manager = PositionManager()
        self.timer(datetime.datetime.now())
    
    def update(self):
        """
            Receive Data,
            Manage Positions
            Check for new trades
            Send Data
            Log
        """
        MT4Connection()

    
    def kill(self):
        self.alive = False

