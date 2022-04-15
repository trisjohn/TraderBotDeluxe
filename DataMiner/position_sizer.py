
import json

class PositionSizer:
    """
        Given a current acc balance, risk value in percent (<1) or cash_val, determine estimated lot size
        ex.
        bal = 50359
        stop_dist = 25
        risk = .005
        exh =  1/109

        cash_risk = bal * risk
        per_pip = cash_risk / stop_dist * exh * 10
        print(cash_risk, per_pip)
    """
    def __init__(self):
        self.data = []
    
    def get(self, rate, balance, risk, stop_pips, isJPY= True, trades =2):
        """
        rate is CounterCurrency / AccountCurrency
        Change mult to 10 if a JPY pair
        """
        mult=.1 if not isJPY else 10
        cash_risk = risk if risk >= 1 else balance * risk
        cash_risk /= trades
        per_pip = cash_risk / stop_pips
        size = per_pip * rate * mult
        size = 0.01 if size < 0.01 else size
        return size

p = PositionSizer()

if __name__ == "__main__":

    exch = input("Rate of exchange >\t")
    if "/" in exch:
        arr = exch.split("/")
        ex = float(arr[0]) / float(arr[1])
    else:
        ex = float(exch)
    trades = input("Number of trades >\t")
    if trades != "":
        try:
            trades = int(trades)
        except:
            trades = 2
    print(
        p.get(
            ex,
            float(input("\nCurrent balance >\t")),
            float(input("\nRisk value >\t")),
            int(input("\nStop loss distance in pips >\t")),
            input("is jpy? (y)\t") == "y",
            trades
        )
    )
