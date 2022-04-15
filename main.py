
from datetime import datetime
try:
    from lib import config
    print(config.debug)
    from lib import command as com
    from lib import thread
    from lib.meta import *
    from lib.data import flat_float

except ImportError:
    print("Relative import failed!", __name__)

import sys
import time
from tkinter import *
from tkinter import ttk

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

class Processor:
    """
        Handles all processes of automation. 
        Retrieving data, both account and market.
        Receiving key events.
        Doing action based on key events.
        Drawing activity to a GUI.
        Active Display of open orders.
        Automatic stops and lot-sizing based on risk.
        Automatic handling of open orders (exits and trailing stops).
        Log all actions.
    """

    def __init__(self, root, frame):
        self.root = root
        self.frame = frame
        self.now = 0
        self.alive = True
        self.loading = False
        self.is_running = True
        self.char = None
        self.buying = False
        self.selling = False
        self.time_last = time.time()
        self.accept_change = False
        self.meta = Meta()
        self.symbols = []
        self.command_labels = []
        self.updater = None
        self.info = ttk.Label(
                        self.frame,
                        text="Terminal Information",
                        foreground="white",  # Set the text color to white
                        background="black"  # Set the background color to black
                    )
        self.info.grid(row=0,column=0,sticky="n")
        self.canvas = Canvas(self.root, background="white", height=400, width=300)
        self.canvas.grid(row=0,column=2, sticky="e")
        self.init_canvas()
        self.index = 0
        self.curr_val = 0
        self.mod_val = 1
        self.status = 0 # entry status
        self.last_val = 0
        self.buffer = 0 # Give the server time to rest
        self.selected_symbol = ""
        self.symbol_index = 0
        self.selected_edit = "Risk"
        self.hold_begin = 0
        self.time_held = 0
        self.process_time = 0
        self.position_entered = [False, ""]
        self.command_keyed = [False, ""] # True if key is pressed or held, string is messaged to display
        self.com_time = 7
        self.canvas_drawn = False
        self.key_timer = 0
        self.on_new_edit = 0
        self.commands = com.Command() #holds all keys respect to their commands

    def init_canvas(self):
        self.canvas.create_line(0,17,300,17)
        self.canvas.create_line(0,18,300,18)

    def clear_canvas(self):
        self.canvas.delete("timer")
        self.canvas.delete("symbol")
        self.canvas.delete("index")
        self.canvas.delete("profit")
        self.canvas.delete("connect")
        self.canvas.delete("manage")

    def draw_canvas(self):

        # Draw selected symbol

        con_color = "red"
        if self.meta.is_connected:
            con_color = "green"
        
        self.canvas.create_oval(280,380,300,400, fill=con_color)

        timer_text = str(self.now / 60) if self.now % 60 == 0 else str(int(flat_float(self.now / 60, 0)))
        self.canvas.create_text(280,8,text=timer_text + " : " + str(self.now % 60), tag="timer")
        symbol_text = self.selected_symbol
        symbol_x = 40
        if self.meta.is_buying():
            symbol_text += " (Buying)"
            symbol_x = 80
        elif self.meta.is_selling():
            symbol_text += " (Selling)"
            symbol_x = 80
        symbol_text += str(self.meta.time_frame) + "m"
        con_color = "orange" if self.meta.managing else "white"
        coor = (10,380,50,340) if self.now % 5 == 0 else (10, 360, 40, 320)
        coor = (20, 380, 70, 340) if self.now % 10 == 0 else coor
        coor = (30, 390, 80, 350) if self.now % 20 == 0 else coor
        self.canvas.create_rectangle(coor, fill=con_color, tag="manage")
        self.canvas.create_text(symbol_x,8,text=symbol_text, tag="symbol")
        self.canvas.create_text(30, 25,text=self.index, tag="index")
        self.canvas.create_text(280, 25, text=self.meta.current_profit(), tag="profit")


    def begin(self):
        self.loading = True
        self.symbols = read_symbols("watchlist.txt")
        self.loading = False
        self.selected_symbol = self.symbols[0]
        self.listen()
        print("TradeBoi Activated.")
        self.work()

    def edit_risk(self):
        # index now toggles risk
        self.selected_edit = "Risk"
        self.mod_val = 1
        if self.accept_change :
            self.meta.edit_risk(self.curr_val)
            self.accept_change = False

    def edit_stop_dist(self):
        self.mod_val = 0.25
        self.selected_edit = "Loss"
        if self.accept_change :
            self.meta.edit_stop(self.curr_val)
            self.accept_change = False
    
    def edit_take_dist(self):
        self.mod_val = 0.25
        self.selected_edit = "Profit"
        if self.accept_change :
            self.meta.edit_take(self.curr_val)
            self.accept_change = False

    def edit_label(self, txt,col="white"):
        self.info.destroy()
        self.info = ttk.Label(
            self.frame,
            text=txt,
            foreground=col,  # Set the text color to white
            background="black"  # Set the background color to black
        )
        self.info.grid(row=0, column=0, columnspan=3, sticky="n")

    def edit_time_req(self):
        self.selected_edit = "Key Hold Time"
        self.curr_val = 1

    def enter_position(self, dir) :
        print("Entering position:", dir, self.selected_symbol)
        return self.meta.prime_order(dir, self.selected_symbol)

    def check_command(self, c) :
        
        co = self.commands.check(c)
        print("Checking key command...", co)
        if co == 0:
            self.edit_label("Buying")
            self.buying = True
            self.selling = False
        elif co == 1:
            self.edit_label("Selling")
            self.buying = False
            self.selling = True
        elif co == 2:
            self.edit_label("Displaying open positions")
            self.display_positions()
        elif co == 3:
            self.edit_label("Editing Risk")
            self.on_new_edit = 0
            self.edit_risk()
        elif co == 4:
            self.edit_label("Editing Stop")
            self.on_new_edit = 0
            self.edit_stop_dist()
        elif co == 5:
            self.edit_label("Editing Take")
            self.on_new_edit = 0
            self.edit_take_dist()
        elif co == 66:
            # Grab all symbol data
            self.edit_label("Fetching Watchlist Data")
            self.meta.fetch_all_markets()
        elif co == 7:
            self.edit_label("Change Accepted")
            self.accept_change = True
        elif co == 8:
            self.edit_label("Reverted last change")     
            self.index = self.last_val
        elif co == 9:
            self.edit_label("Display all commands")
            self.display_commands()
        elif co == 11:
            self.index += 1 * self.mod_val
            self.edit_label("Incremented " +str(self.index))
        elif co == 22:
            self.index -= 1 * self.mod_val
            self.edit_label("Incremented " +str(self.index))
        elif co == 99:
            self.edit_label("Editing key press time requirement")
            self.edit_time_req()
        
        if self.index < 0:
            self.index = 0
        

    def key_pressed(self, e):    
        if self.char == e.char :
            self.time_held = self.now - self.hold_begin
            val = "Processing"
            for _ in range(self.time_held):
                val += "."
            
            if(self.time_held >= self.commands.time_req):
                val = " ] Primed (Release Key to Confirm)"
            self.command_keyed = [True, "Command [ " + e.char + val]
        elif e.keysym == 'Escape':
            self.alive = not self.alive
            print("TradeBoi is alive:", self.alive)
            if self.alive: self.work()
            else: self.edit_label("Offline.", "red")
        else :
            self.char = e.char
            co = self.commands.check(self.char)
            if co == 6:
                self.edit_label("Canceling Entry", "yellow")
                self.buying = False
                self.selling = False
                self.meta.data.entry = None
            elif co == 10:
                self.symbol_index += 1
                if self.symbol_index >= len(self.symbols) : self.symbol_index = 0
                self.selected_symbol = self.symbols[self.symbol_index]
            elif co == 12:
                self.symbol_index -= 1
                if self.symbol_index < 0 : self.symbol_index = len(self.symbols)-1
                self.selected_symbol = self.symbols[self.symbol_index]
            else:
                self.command_keyed = [True, "Pressed command: " + e.char]
                self.hold_begin = self.now


    def key_released(self, e):

        if(self.time_held >= self.commands.time_req):
            self.check_command(e.char)
            self.key_timer = 3
            

        #print('released', e.char, 'after', self.time_held)
        self.time_held = 0
        self.char = None
        self.hold_begin = 0
        self.command_keyed = [False, ""]

    def listen(self):
        self.frame.bind("<KeyPress>", self.key_pressed)
        self.frame.bind("<KeyRelease>", self.key_released)
        #self.frame.pack()
        self.frame.focus_set()

    def work(self):
        # Seperate thread for these
        self.start_time = datetime.datetime.now()
        side_thread(15, "Work Thread", self.work_timer)
        self.timer()
        

    # Loops while is alive
    def work_timer(self):
        # QUARATINE: Figure out how to keep this thread alive even when self.update ends. Should only be disposed of if client killed. Loop?
        if not self.updater:
            print("No updater thread, rebuilding...")
            self.updater = thread.NewThread(15, "Updater", self.update)
            self.updater.daemon = True
            self.updater.start()
        elif not self.updater.is_alive():
            print("Updater thread completed, deleting...")
            self.updater = None

    # timer
    def timer(self):
        if self.alive:
            if time.time() - self.time_last >= 1:
                self.time_last = time.time()
                self.draw_timer()
                self.now += 1
                self.frame.after(1000, self.timer)
            else:
                time.sleep(0.33)
                self.timer()                
    
    # Loops while is alive
    def draw_timer(self):
        if self.alive:
            self.clear_canvas()
            self.draw()
            

    # Do process
    def update(self):
        
        # On update run server, but server should return if the server is still running
        # Run Server takes care of all maitenence, managing positions, fetching market, fetching acc
        # Only thing outside of run server is enter position, which is still queued by run server
        curr = self.now

        while self.alive:
            
            if curr == self.now: continue
            self.is_running = True
            curr = self.now

            if self.buffer == 0:
                if self.meta.run_server():
                    self.buffer = 3
                    self.meta.new_command("account")
                    self.meta.fetch_market(self.selected_symbol)
                    self.meta.new_command("position")
                    self.is_running = False
                    print("Server completed.")
            else: self.buffer -= 1

            status = 0

            # Attempt entry
            if not self.is_running:
                status, side, sym = self.meta.attempt_entry(self.selected_symbol)
                print("Entry Attempt:", side, sym) if side > -1 else print("No current entry")
            
            if status > 0:
                name = "New Position Entered!"
                name = name + " Sell on " if side == 1 else name + " Buy on "
                self.position_entered = [True, name+sym]
            elif status < 0:
                name = "Position Failed to Enter: " + str(abs(status)) + "!"
                name = name + " Sell on " if side == 1 else name + " Buy on "
                self.position_entered = [True, name + sym]

            # check for any current commands, load time and when time is completed load the command
            if(self.buying or self.selling):
                self.process_time += 1
                if self.process_time >= self.com_time:
                    val = 0 if self.buying else 1
                    self.process_time = 0 
                    if(self.enter_position(val)):
                        self.key_timer = 3
                        self.selling = False
                        self.buying = False
            
            if self.on_new_edit == 0:
                self.last_val = self.index
                self.index = round(self.index) 
                self.on_new_edit += 1
            else:
                self.on_new_edit += 1
            
            
        
        #self.data = data.Data()

    # Draw terminal
    def draw(self):
        #self.pack()
        
        self.draw_canvas()
        
        if self.key_timer <= 0:
            c = "white"
            buy = self.meta.is_buying()
            sell = self.meta.is_selling()
            if buy:
                c = "green"
            elif sell:
                c = "red"
            s = "Entry Processing!" if buy or sell else "Processing..."
            if not self.command_keyed[0]:
                if not self.is_running and not buy and not sell:
                    if not self.meta.data.has_market(self.selected_symbol):
                        s = "No market data loaded for symbol " + self.selected_symbol + ". Press / to retry." 
                        c = "orange"
                    else:
                        s = "TradeBoi Ready"
            else:
                c = "blue"
                s = self.command_keyed[1]
            
            self.edit_label(s, c)
        else:
            self.key_timer-=1

        # check for any current commands, load time and when time is completed load the command
        if(self.buying or self.selling):
            name = "Processing Buy (press c to cancel) " if self.buying else "Processing Sell (press c to cancel) "
            self.edit_label(name + str(flat_float(self.process_time / self.com_time * 100,0)) + "%", "cyan")
            if self.process_time >= self.com_time:
                name = name[0:10] + " Entry"
                self.edit_label(name)

        if self.position_entered[0]:
            self.edit_label(self.position_entered[1], col="orange")
            self.key_timer = 5
            self.position_entered = [False, ""]


    def display_commands(self):
        # display all commands and their respective keys
        arr = self.commands.display()
        
        if len(self.command_labels) < 1 :
            count = 0
            print("Showing commands.")
            for a in arr:
                name = ttk.Label(
                    self.frame,
                    text=a[0] + " =>",
                    foreground="black",  # Set the text color to white
                    background="white"  # Set the background color to black
                )
                val = ttk.Label(
                    self.frame,
                    text=a[1],
                    foreground="red",
                    background="white"
                )
                name.grid(row=1+count, column=1, sticky="w")
                val.grid(row=1+count, column=1, sticky="e")
                count+=1
                self.command_labels.append(name)
                self.command_labels.append(val)
        else:
            for c in self.command_labels:
                c.destroy()
            self.command_labels = []

    def display_positions(self):
        #draw positions
        print("Drawing all open positions.")
        
        if self.canvas_drawn == False:
            self.canvas.create_line(0,200,300,200)
            self.canvas.grid(row=0, column=1, sticky=(E))
            self.canvas_drawn = True
        else:
            self.canvas.grid_forget()
            self.canvas.delete()
            self.canvas_drawn = False
    def display_market(self):
        # Displays the market of the current selected symbol
        return
    # Shut down
    def kill(self):
        self.meta.save_logs()
        self.alive = False

root = Tk()
root.title("Trade Boi Deluxe")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N))
p = Processor(root, mainframe)
p.begin()
root.mainloop()
