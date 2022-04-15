from random import *


# Given a win_rate [float] and number of trades [x] or fixed win/loss pattern [string], simulate trades over x intervals
class Balance_Tester:
    def __init__(self, balance, arg):
        self.balance = balance
        self.start = balance
        if isinstance(arg, str):
            self.len = len(arg)
            self.pattern = arg
            self.fixed = True
        elif isinstance(arg, list):
            self.len = arg[1]
            self.pattern = arg[0]
            self.fixed = False
        else:
            raise Exception ('Error', 'Inavlid Arguments EXAMPLE:  LWLWLWLW or [0.65, 100] ')
    
    def loss(self, r):
        self.balance=  self.balance * (1 - r)
        #print(".", end="", sep="")

    def win(self, r):
        val = uniform(.4, 1.5) * r

        self.balance= self.balance * (1 + val)
        #print("|", end="", sep="")

    def run(self):
        best = 0.00
        highest = 0.0
        for risk in range(1, 10):
            risk = risk / 100
            self.balance = self.start
            if not self.fixed:
                for x in range(self.len):
                    if random() < self.pattern:
                        self.loss(risk)
                    else:
                        self.win(risk)
                        
            else:
                for x in self.pattern:
                    if x == "L":
                        self.loss(risk)
                    elif x == "W":
                        self.win(risk)
                    else:
                        None

            if self.balance > highest:
                highest = self.balance
                best = risk
        print(str(best*100) + '%' + " for " + str(round(highest/self.start * 100)) + '%'+ " ROI")
        return (best, highest/self.start)


ratio = 65
x = 10
print("Test for ratio:", ratio, end="\r\n\r\n")
ratio = ratio / 100
for i in range(1,10):
    val = randrange(x, 100)
    print("after", val, "trades, best ratio:")
    (risk, roi) = Balance_Tester(1000, [ratio, val]).run()
    print(risk, roi)

    
    
    
