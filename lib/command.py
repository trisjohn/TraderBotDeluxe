class Command:
    def __init__(self):
        self.buy = "b"
        self.sell = "s"
        self.see_orders = "o"
        self.edit_risk = "r"
        self.edit_stop_dist = "l"
        self.edit_take_dist = "t"
        self.inc_symbol = "'"
        self.dec_symbol = ";"
        self.time_req = 2 
        self.cancel = "c"
        self.accept = "]" # accept edited change
        self.revert = "[" # revert to previous change
        self.kill = "k"
        self.inc = "="
        self.dec = "-"
        self.fetch_data = "/"
        self.display_commands = "d"

    def check(self, c):
        if(c == self.buy):
            return 0
        elif(c == self.sell):
            return 1
        elif(c == self.see_orders):
            return 2
        elif(c == self.edit_risk):
            return 3
        elif(c == self.edit_stop_dist):
            return 4
        elif(c == self.edit_take_dist):
            return 5
        elif(c == self.cancel):
            return 6
        elif(c == self.inc):
            return 11
        elif(c == self.dec):
            return 22
        elif c == self.fetch_data:
            return 66
        elif(c == self.accept):
            return 7
        elif(c == self.revert):
            return 8
        elif(c == self.display_commands):
            return 9
        elif(c == self.inc_symbol):
            return 10
        elif(c == self.dec_symbol):
            return 12
        else:
            return 99 # time_req before initiating
    
    def display(self):
        # return an array of commands + current keys
        arr = []
        keys = ["buy", "sell", "show positions", "edit risk", "edit stop distance", "edit take distance", "edit key hold time", "cancel",
                "accept change", "revert change", "increment", "decrement", "display commands"]
        
        arr.append([keys[0], self.buy])
        arr.append([keys[1], self.sell])
        arr.append([keys[2], self.see_orders])
        arr.append([keys[3], self.edit_risk])
        arr.append([keys[4], self.edit_stop_dist])
        arr.append([keys[5], self.edit_take_dist])
        arr.append([keys[6], str(self.time_req)])
        arr.append([keys[7], self.cancel])
        arr.append([keys[8], self.accept])
        arr.append([keys[9], self.revert])
        arr.append([keys[10], self.inc])
        arr.append([keys[11], self.dec])
        arr.append([keys[12], self.display_commands])
        
        return arr