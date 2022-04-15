import datetime

def remove_duplicates(arr):
    """
        Removes all duplicates or msgs of 78% similarity
    """
    new_arr = []
    for a in arr:
        if a in new_arr: continue
        for b in arr:
            if b in new_arr: continue
            if b.msg == a.msg:
                first, sec = a.msg, b.msg
                l = len(b.msg)
                for i in range(l, round(.78 * l)):
                    if sec[:i] in first: new_arr.append(a)
    return new_arr
                    
            
class Logger:
    """
        Save info into various logs, within the log folder.
        Takes in an array of Entries, sorts them via level, then sorts them via date time, grouping them in hour intervals
        cleaning any like Entries
    """
    def clean_arrays(self):
        remove_duplicates(self.info)
        remove_duplicates(self.warn)
        remove_duplicates(self.error)
        remove_duplicates(self.fail)

    def __init__(self, log_dir_path, data):
        self.info = []
        self.warn = []
        self.error = []
        self.fail = []
        for d in data:
            if d.status == 0:
                self.info.append(d)
            elif d.status == 1:
                self.warn.append(d)
            elif d.status == 2:
                self.error.append(d)
            else:
                self.fail.append(d)
        self.clean_arrays()
        self.group_arrays()
        self.to_file()

class Entry:
    """
        An entry for logger, has a datetime, critical level, and message
        Critical Level is from 0-3 Where 0 is info, 1 is warning, 2 is error, 3 is critical failure
    """
    def __init__(self, msg, dt, level=0):
        self.val = msg
        self.time = dt
        self.status = level

def entry(msg):
    """
        Take in a msg and return an Entry object
    """
    level = 0
    if "Warning" in msg or "warning" in msg:
        level = 1
    elif "Error" in msg or "error" in msg:
        level = 2
    elif "Critical" in msg or "critical" in msg:
        level = 3
    
    curr_dt = datetime.datetime.now()

    return Entry(msg,curr_dt,level)