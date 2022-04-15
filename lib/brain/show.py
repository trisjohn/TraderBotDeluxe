import matplotlib.pyplot as plt

import numpy as np
from lib import *

data = read("XAUUSD_1")

asks = [np.array([], dtype=np.datetime64), np.array([], dtype=np.float64)]
bids = [np.array([], dtype=np.datetime64), np.array([], dtype=np.float64)]
is_ask = False
for d in data:
    if d == "ask":
        is_ask = True
    elif d == "bid":
        is_ask = False
    elif type(d) is np.float64:

        if is_ask:
            asks[1] = np.append(asks[1], np.array([d]))
        else:
            bids[1] = np.append(bids[1], np.array([d]))

    else:
        
        if is_ask:
            try:
                asks[0] = np.append(asks[0], np.array([d], dtype=np.datetime64))
            except:
                print(asks[0], asks[1], "cant append to asks")
                exit()
        else:
            try:
                bids[0] = np.append(bids[0], np.array([d], dtype=np.datetime64))
            except:
                print(bids[0],bids[1], "can't append to bids")
                exit()


### MEAN TESTS

# ask_mean = ema(asks[1], 200)
# bid_mean = ema(bids[1], 200)

# empty = []
# for i in range(len(asks[0]) - len(ask_mean)):
#     empty.append(None)
# ask_mean = np.insert(ask_mean,0,empty)

# empty = []
# for i in range(len(bids[0]) - len(bid_mean)):
#     empty.append(None)
# bid_mean = np.insert(bid_mean,0,empty) 

# plt.plot(asks[0], ask_mean,color ='green', label = "Ask Mean")
# plt.plot(bids[0], bid_mean, color="red", label ="Bid mean")
ask_mean = ema(asks[1],200)
plt.plot(asks[0][len(asks[0]) - len(ask_mean):], ask_mean, color = 'violet', label = 'Ask data', alpha=0.7, linewidth=0.5)
bid_mean_slow = ema(asks[1],500)
plt.plot(asks[0][len(asks[0]) - len(bid_mean_slow):], bid_mean_slow, color = 'red', label = 'Ask data', alpha=0.7, linewidth=0.5)
# plt.plot(bids[0], bids[1], color = 'blue', label='Bid data',alpha=0.5, linewidth=0.5)
plt.legend()
plt.show()