
### Connect and send/receieve messages on a local port
import json
import threading

class NewThread(threading.Thread):
    def __init__(self, id, name, function, args=None):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.function = function
        self.args = args
    
    def run(self):
        print("Running thread", self.name)
        self.function(self.args)
        self.join()

class MT4Connection:

    def reach(self, msg):
        ### send msg to client, save inventory message, increment interaction

        self.iteration += 1
    def __init__(self):
        ### Establish connection to server
        ok = json.dumps({'status': 'test'})
        self.iteration = 0
        self.inventory = []
        print("Simulate connection...")
        # thread = NewThread(101, "MT4 Connection", self.reach, ok)
        # thread.run()

    def command(self, args):
        """ args is key, dict """
        last = self.iteration
        if args.key == 'buy' or args.key == 'sell':
            # check args.value dictionary is correct
            #{'symbol': ######, 'side'=0, 'price'=0(limit at ask), 'stop'= 0.0, 'take'=0.0, 'lots'=0.01, 'number'=2, 'cancel'=0(automatically cancel on next close)}
            for k,v in args.values:
                if k == 'symbol' and (type(v) is not str or len(v) != 6):
                    raise RuntimeWarning(args, "Improper Symbol for new entry.")
                elif k == 'side' and (v != 0 and v != 1):
                    raise RuntimeWarning(args, "Invalid side given.")
                elif k == 'price' and v == 0:
                    print("No price value given, will place", args.key, f"limit order at {'bid' if args.key == 'sell' else 'ask'}")
                elif k == 'stop' and (v == 0 or v < 0):
                    print("No stop value given, will place", args.key, f"stop loss above/below last {'high' if args.key == 'sell' else 'low'}")
        elif args.key == 'position':
            #{'symbol': ###### (if"" return all positions), 'stop':0(don't update stop), 'close':0(if price, place limit)}
            symb = args.values.symbol
            for k,v in args.values:
                if k == 'symbol' and len(v) == 0:
                    print("All position info requested from MT4.")
                    break
                if k == 'symbol' and (type(v) is not str or len(v) != 6 ):
                    raise RuntimeWarning(args, "Improper Symbol for position.")
                elif k == 'stop' and v != 0:
                    print(symb, "position stop to be updated at", v)
                elif k == 'close' and v != 0:
                    print(symb, "position to be closed at", v)
        
                
        thread = NewThread(101, "MT4 Connection", self.reach, json.loads(args.values))
        thread.run()
        thread.join()
        
        
    def check(self, prev):
        ### given a previous iteration, return last item if new iteration
        if prev < self.iteration:
            return self.inventory[len(self.inventory)-1], self.iteration
        
        return None, prev