### Version 2 of MT4 trade manager
# Built out of terminal not a glitchy gui
print(__package__,__file__,__name__)
# Everything is sent in json, for easy data transfer
from lib.timerlogger import *
from lib.menu import *
import json

m = Menu(input('Enter Menu save path > '))

while m.alive:
    TimerLogger(m.start())
    time.sleep(1)

print("metyBoi shut down. Good Bye!")