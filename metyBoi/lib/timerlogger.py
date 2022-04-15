# Will take all info and save it to file, as well as timing the various processes

import time
import os, shutil
import datetime


def clear_folder(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



class TimerLogger:
    """ Starts a function, logging its return and speed every interval minutes """
    def __init__(self, data):
        
        t = datetime.datetime.now()
        print("Simulate timer logger.", t.isoformat())
        # os.chdir(r'C:\Users\x7pic\Documents\Advance Momentum\TradeBoiDeluxe\metyBoi\lib\logs')
        # with open(str(t.date), 'a') as f:
        #     f.write(f"[{t.hour}:{t.minute}:{t.second}] {data}")
        
        

print(__package__, __name__)