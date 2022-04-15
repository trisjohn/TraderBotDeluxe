# Responsible for gathering relevant market data, which would be the bars we are entering on
# Saves bars to file to gather later
# Finds position and saves result

# Reach out to server for open positions
#   tickets []
#   opentime

# Reach out to server for the last N bars beginning at nearest bar to open time
#   emalong
#   emashort
#   atr
#   close
#   high
#   low
#   open
#   volume

# closeTime (of just closed position)
# profit (of just closed position)

import socket


class Pipe:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 8081))
        self.socket.listen(5)
        self.socket.settimeout(30)
    def renew(self):
        if self.socket:
            self.socket.close()
            del self.socket
        else:
            del self.socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 8081))
        self.socket.listen(5)
        self.socket.settimeout(30)
    def send(self, msg):
        conn, addr = self.socket.accept()
        with conn:
            print('Connected to Send', addr)
            print(conn.send(msg.encode()), "bytes sent")
                
    def receive(self):
        conn, addr = self.socket.accept()
        with conn:
            print('Connected to Receive', addr)
            data = ""
            while True:
                try:
                    print("Preparing to recieve...")
                    data = conn.recv(1).decode()
                    print("receiving...", data, end="_")
                except:
                    raise Exception("connection broken")
                if data == "?":
                    break
        return data

class Gather:
    def __init__(self):
        self.pipe = Pipe()
        self.uses = 0

    # connect to client and send val, return the string
    def reach(self, val):
        if self.uses > 0: self.pipe.renew()
        self.pipe.send(val)
        print(self.pipe.receive())
        self.uses+=1

g = Gather()
g.reach("Fuck you")
g.reach("Bitch ass fucking bitch boy")