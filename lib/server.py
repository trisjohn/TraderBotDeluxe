from lib.thread import new_thread
import struct
import socket
import datetime
from lib.data import Dictionary
from collections import namedtuple
"""
    Flags:
    buy/sell:symbol:vol:sl:tp
    modify:symbol:newStop
    close:symbol
    account:freemargin:equity:profit
    position:ticket:open:lots:sl:tp:profit:symbol
 
"""
Candle = namedtuple('Candle', 'high open low close volume emashort emalong atr')

class Flag:
    def __init__(self, name):
        self.name = name
        self.values = []
    
    def add(self, val):
        if not isinstance(val, list):
            self.values.append(val)
        else:
            self.values.extend(val)
        # print("Flag object built:", self.name, self.values)
    
    def get(self):
        s = self.name
        for v in self.values:
            s += ":" + str(v)
        return s + "\r\n"
    
    def digest(self, data):
        # turn data into values
        #print(self.name, "digesting", data)
        
        if not data:
           print("Error. No Data to digest", self.name) 
           return    

        val = []
        for da in data.split("string#}:"):
            # print("Digesting...", da)
            if da == "" : continue
            dat = da.split(":")
            arr = []

            for x in dat :
                d = x.split("#")
                if d[0] == "string":
                    arr.append(d[1])
                elif d[0] == "float":
                    arr.append(float(d[1]))
                elif d[0] == "int":
                    arr.append(int(d[1]))
            
            val += arr
        #print("Values successfully digested.", val)
        
        self.values = val if len(val) > 1 else val[0]
        # print(self.name, "data received from client", self.values)
    
    def clean(self):
        clean_arr = []
        clean_arr.append(self.name)
        
        for x in self.values:
            clean_arr.append(x)
        
        # print(clean_arr[0], "cleaned.")
        return clean_arr

class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 8080))
        self.socket.listen(5)
        self.socket.settimeout(30)
        self.client = None

        self.data = None
        # flags
        self.buying = None
        self.selling = None
        self.modifying = None
        self.closing = None
        self.pos_info = None
        self.symbol_info = []
        self.error_info = None
        self.acc_info = None
        self.chart_info = []
        
        self.dataReady = False

    def reset_settings(self):
        self.client = None

        self.data = None
        # flags
        self.buying = []
        self.selling = []
        self.modifying = None
        self.closing = None
        self.pos_info = None
        self.symbol_info = []
        self.acc_info = None
        self.dataReady = False
    # Send data to client to initiate an action
    # Args are the necessary data that maybe required for the respective action
    def new_command(self, c, args = []): # position

        if c == "buy":
            # symbol, vol, sl, tp
            b = Flag("buying")
            b.add(args)
            self.buying.append(b)
        elif c == "sell":
            
            s = Flag("selling")
            s.add(args)
            self.selling.append(s)
        elif c == "modify":
            self.modifying = Flag("modifying")
            self.modifying.add(args)
        elif c == "close":
            self.closing = Flag("closing")
            self.closing.add(args)
        elif c == "account":
            self.acc_info = Flag("account")
        elif c == "position":
            self.pos_info = Flag("position")
        else:
            sym = Flag(c)
            sym.add(args)
            self.symbol_info.append(sym)

    # Return data in a special format for the chart object
    def get_chart(self):
        # build market arrays
        arr = []
        # data is constructed as such symbol:timeframe:ask:bid:totalbars:opens[]:closes[]:highs[]:lows[]:longmeans[]:shortmeans[]:volumes[]:atrs[]
        try:
            for val in self.chart_info:
                v = val.values
                a = Candle(v[0],v[1],v[2],v[3], v[4], v[5], v[6], v[7])
                arr.append(a)
        except:
            print("Error building Chart data.")
        return arr

    def get_data(self):
        account = None
        position = None
        symbol = None
        error = None

        if self.acc_info:
            account = Dictionary("account",self.acc_info.clean())

        if self.pos_info:
            positions = []
            p = []
            # print("Constructing Positions.")
            for x in self.pos_info.values:
                # print(x)
                if isinstance(x, str):
                    if len(x) == 6:
                        if len(p) > 0 : positions.append(p)
                        p = [] 
                p.append(x)
            if len(p) > 0: positions.append(p)
            position = Dictionary("position",positions)
        
        
        if len(self.symbol_info) > 0:
            symbol = Dictionary("symbols", [])
            for s in self.symbol_info:
                sym = s.clean()
                name = sym[0]
                sym.pop(0)
                symbol.add(Dictionary(name,sym))
        
        if self.error_info:
            error = Dictionary("error", self.error_info.clean())
        
        self.reset_settings()
        
        if account or position or symbol or error: print("\nServer data formatted.")
        return account, position, symbol, error

    def recieve(self):
        chunks = []
        bytes_recd = 0
        msg_len = 0
        MSGLEN = 4096
        # print("Receiving Data...")
        while bytes_recd < MSGLEN:
            try:
                chunk = self.client.recv(1)
            except:
                print("ERROR! Reciever broken. Client=", self.client)
                break
            msg_len += 1
            # print("<", end="")
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            
            if chunk == b'>':
                # print("\r\nEnd of Received data.")
                break 

            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        msg = b''.join(chunks)    
        return msg.decode("utf-8")     
    
    def send_string(self, msg):
        # print("Sending Message to Client.\r\n")
        m = msg.encode('utf-8','strict')
        totalsent = 0
        while totalsent < len(m):
            sent = self.client.send(m[totalsent:])
            print("-->", end="")
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        # print("\r\n")
        # print("Message to client completed.",msg)

    def reconnect(self):
        if not self.socket: return 
        e = self.socket.connect_ex(('localhost', 8080))   
        if e != 0:
            print("No connection to client error:", e)
            # self.socket.bind(('localhost', 8080))
            # self.socket.listen(5)
            # self.socket.settimeout(10)
            # print("Retrying connection.")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('localhost', 8080))
            self.socket.listen(5)
            self.socket.settimeout(30)
            # print("Socket rebound.")

    def catch(self):
        # print("Running server to receive data.")
        data = ""
        # recieve acc info
        data = self.recieve()
        res = data.split("]")
        self.symbol_info = []
        #print(res) if len(res) > 1 else print("*", end="") 
        for d in res:
            c = d.split("[")  
            if c[0] == "" or c[1] == "": continue                               
            # print("Grabbing data from client:", c)
            if c[0] == "account" :
                self.acc_info = self.acc_info if self.acc_info else Flag("account")
                self.acc_info.digest(c[1])

            # recieve position info
            elif c[0] == "position" :
                # print("Received Position info.")
                self.pos_info = self.pos_info if self.pos_info else Flag("position")
                self.pos_info.digest(c[1])
            
            # receive symbol info
            elif "symbol=" in c[0]:
                #print("Received symbol info.", c[0])
                symbol = c[0].split("=")[1]
                sym = Flag(symbol)
                sym.digest(c[1])
                self.symbol_info.append(sym)
            
            elif c[0] == "errors":
                self.error_info = Flag("error")
                self.error_info.digest(c[1])
            

    def begin(self):
        
        # Unready the data
        self.dataReady = False

        # Open up a communication between the client

        # Do whatever tasks that are flagged for by the trade boi

        try:
            # print("Running server to send")
            if not self.socket:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind(('localhost', 8080))
                self.socket.listen(5)
                self.socket.settimeout(30)
            (clientsocket, address) = self.socket.accept()
            self.client = clientsocket
            # print(address)
            # print("Client accepted.") if self.client else None
            data = ""
            # Send for account info
            if self.acc_info :
                data +="account\r\n"
                data += "]"
            # send for position info
            if self.pos_info :
            # send for symbol info
                data +="position\r\n"
                data += "]" 
            # send buy/sell order
            if self.buying :
                for b in self.buying:
                    data += b.get()
                    data += "]"
            if self.selling :
                for s in self.selling:
                    data += s.get()
                    data += "]"
            # modify order
            if self.modifying :
                data += self.modifying.get()
                data += "]"
            # close order
            if self.closing :
                data += self.closing.get()
                data += "]"

            # send for symbol
            if self.symbol_info:
                for s in self.symbol_info:
                    data += "!" + s.get()


            # print("Data sending...")
            if data != "":
                new_thread(400,"Sender",self.send_string, data)
            # print("Data sent.")
            #self.client.shutdown(1)

        except socket.timeout as t:
            print("Send: Timeout error: %s. Is MT4 Client online?" % t)
            return

        except socket.error as exc:
            print("Send: Caught on exception : %s @ " % exc, address)

        try:
            if self.client:
                new_thread(401, "Receiver", self.catch)
            else:
                print("No client connected to recieve data from.")
            
            # Data is finished received
            self.dataReady = True

        except socket.timeout as t:
            print("Receieve: Timeout error: %s. Is MT4 Client online?" % t)

        except socket.error as exc:
            print("Recieve: Caught exception : %s @ " % exc, address)

        self.socket.close()
        self.socket = None


# Server Test
# s = Server()
# # s.new_command("sell", ["GBPUSD", 1.00, 1.3990, 1.394])
# # s.new_command("position")
# s.new_command("EURJPY", [96,9,55, 15])
# s.new_command("EURUSD", [96,9,55, 15])
# s.new_command("USDJPY", [96,9,55, 15])
# # s.new_command("account")
# s.begin()
# _, _, symb, _ = s.get_data()
# print(symb)