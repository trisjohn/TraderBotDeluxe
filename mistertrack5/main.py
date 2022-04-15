# MT5 Variant, to build bot on first. First we shall rebuild the trade manager.

# Terminal only application

"""
>> TO DO:

Fix trade function in meta. Call trade when user inputs buy or sell.
Trade should ask for a stop value, if none is given, assumes 1.5 * atr, then calculates risk
Make sure position manager gets correct info
Ensure position manager modifies orders correctly


"""

from collections import namedtuple
from json.decoder import JSONDecodeError
import os
import json
from mistertrack5.order import *
from mistertrack5.position import *
from mistertrack5.account import *

Choice = namedtuple('Choice', 'about value children') # Next is next choice, previous is previous choice Choice A > choice a > choice 1
                                                                                                    #   Choice B > choice b > choice 2

class Menu:
    def __init__(self):
        self.choices = []
        self.current = Choice("Nothing selected.", "none", None)

    def choices_string(self):
        s = ""
        i = 1
        for x in self.choices:
            s += str(i)+"."+x.value+" "
        return s
    
    def show(self, choices, sub=False):
        i = 0
        if  len(choices) < 1: 
            print("No Menu items. Press Enter twice to add new.") if not sub else print("Sub-menu is empty. Press any key to continue.")
            return
        for c in choices:
            i+=1
            print(i, ".", c.value, "[ ---", c.about, "]")

    def add_choice(self, new_choice):
        if len(new_choice) < 3:
            self.choices.append(Choice(new_choice[1], new_choice[0], []))
        else:
            parent = new_choice[0]
            val = new_choice[1]
            about = new_choice[2]
            for x in self.choices:
                if x.value == parent:
                    arr = x.children
                    arr.append(Choice(about,val,None))
                    x = Choice(x.about, x.value, arr)

    def check_exit(self, val):
        if val == "exit" or val == "e" or val == "end" or val == "quit":
            print("Program Terminated.") 
            exit()

    def read_sub_menu(self, name, val):
        if name == "New Order":
            OrderEntry(val, input("Enter Symbol = "))
        elif name == "Order Management":
            OrderManage(val, input("Enter New Value = "))
        elif name == "Account Info":
            AccountInfo(val)

    def check_choice(self, i, choices):
        i = i - 1
        selected = choices[i]
        print(selected.value, "selected.")
        self.show(selected.children, True)
        val = input(selected.value + " > ")
        ans = val
        self.check_exit(val)
        self.read_sub_menu(selected.value, val)


    def get_input(self):
        val = input("> ")
        if self.current.value == "none": self.current = Choice("New selection", val, None)
        print("Your current selected menu option:", self.current)
        if val == "" and self.current.value == "":
            try:
                self.add_choice(input("Add new Menu value (parent_name:value:description)\n>").split(":"))
            except:
                print("invalid input.")
        elif val == "save":
            ans = input("Are you sure you want to save the menu? (y)\n")
            if ans != "y": return
            self.save_menu()
        elif val == "delete":
            ans = input("Which menu item to delete? Type only the #.\n"+self.choices_string()+"\r\n")
            n = int(ans)
            if n < 1 or n > len(self.choices): print("Invalid choice to delete.")
            to_delete = self.choices[n-1]
            print(to_delete, "deleted.")
            self.choices.remove(to_delete)
        else:
            self.check_exit(val)
            ans = int(val)
            if ans < 1 or ans > len(self.choices):
                print("Invalid option. Must be 1 -", len(self.choices))
            self.check_choice(ans, self.choices)

    def save_menu(self):
        os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')

        f = open("menu_choices_mt5.txt", 'w')
        for d in self.choices:
            f.write(json.dumps(d._asdict())+"\n")
        f.close()
    
    def load_menu(self):
        self.choices= []
        print("Loading menu...")
        os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\lib\brain\memory')
        try:
            with open("menu_choices_mt5.txt", 'r') as f:
                for l in f:
                    n = json.loads(l.strip("\n"))
                    self.choices.append(Choice(**n))
  
            print(len(self.choices), "options found.")
        except Exception as e:
            print("No menu saved.", e, n)
            
m = Menu()
m.load_menu()
while True:
    m.show(m.choices)
    m.get_input()