import threading

class TestMaxGrowth():
    def __init__(self, days):
        self.val = 500
        self.growth = 1.05
        self.days = days
    def begin(self):
        for x in range(1,self.days):
            self.val = self.val * self.growth
            if x % 2 == 0:
                self.val = self.val * .95
        print("Balance after",self.days,"=",self.val)


class NewThread(threading.Thread):
    def __init__(self, id, name, function, args=None):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.function = function
        self.args = args
    def run(self):
        print("Starting new Thread:", self.name, self.args)
        if getattr(self.function, "begin", None) != None:
            self.function.begin()
        else:
            self.function() if not self.args else self.function(self.args)          
        # print("Thread completed:", self.name)
    def wait(self):
        print("Waiting on thread:", self.name)
        self.join(30)
        if self.isAlive():
            return
    def launch(self):
        self.start()
        self.wait()

# Spawn a new thread, assumes function is an object that has the begin method
def new_thread(id, name, function, args=None):
    t = NewThread(id,name,function, args)
    t.launch()
    return t

# Spawn a side thread, assumes function has the begin method.
def side_thread(id, name, function):
    t = NewThread(id, name, function)
    t.start()
    

#Tests
# t0 = TestMaxGrowth(20)
# t1 = TestMaxGrowth(80)
# t2 = TestMaxGrowth(160)
# t3 = TestMaxGrowth(240)

# new_thread(1,"test_7days",t0)
# new_thread(2,"test_14days",t1)
# new_thread(3,"test_21days",t2)
# new_thread(3,"test_21days",t3)