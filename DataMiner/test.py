import pandas as pd
import numpy as np

labels = ('open', 'high', 'low', 'close', 'volume')
arr = []
for x in range(25):
    o = pd.ra

# df = pd.DataFrame([('Foreign Cinema', 'Restaurant', 289.0),
#                    ('Liho Liho', 'Restaurant', 224.0),
#                    ('500 Club', 'bar', 80.5),
#                    ('The Square', 'bar', 25.30),
#                    ('The Lighthouse', 'bar', 15.30),
#                    ("Al's Place", 'Restaurant', 456.53)],
#            columns=('name', 'type', 'AvgBill')
#                  )

def test_kill(d):
    arr = d['AvgBill'] - 102
    return arr

df = df.apply(test_kill, axis=1)
print(df)