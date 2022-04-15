
"""
TO DO:
    Finish swing low trendline cleaner
    Create swing high trendline creater and cleaner
"""

class Line:
    """
    Builds a linear function given two pairs of x,y
    """
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.slope = (y2 -y1) / (x2 -x1)
        self.b = y1 - self.slope * x1
    
    def get(self, x):
        return self.slope * x + self.b


def get_low_swing_trends(df):
    """
    Returns an array of swing low trend lines, each obeying the following rules:
    A. No interesection of other candles in between the two points (Except in case c)
    B. Only one trend line inbetween any given set of dates
    C. If the intersection of a candle would be above its close
        and the latter anchor point is before the intersection, 
        draw the trendline with same slope through that candle
    """
    trends = []
    a = None
    b = None
    i = 0
    l = len(df['low']) - 1

    # Build the initial group of trendlines
    # [a, b] where a and b are (Index of price, price)
    for f in df['low']:
        print(f"Iterating through lows...{i} of {l} {f} is {df['low'][i]}")
        if i == l: break
        if i == 0:
            i+=1
            continue
        if f < df['low'][i-1] and f < df['low'][i+1]:
            a = (i, f)
            for j in range(i+1,l):
                print("searching for next swing", j)
                low = df['low'][j]
                if low < df['low'][j-1] and low < df['low'][j+1]:
                    b = (j, low)
                    break
            if a and b:
                print("new swing low trendline found", [a,b]) 
                trends.append([a,b])
        i += 1
    
    trend_lines = []
    # Check each trendline for intersection
    for a,b in trends:
        # Extrapolate the points
        x1, y1 = a
        x2, y2 = b
        line = Line(x1,y1,x2,y2)
        new_point = b # This is the furthest swing low point along the trendline that has no interceptions
        for x in range(x1+1,l):
            # Check the trend line for any intercepts
            bad_line = False
            y_val = line.get(x)
            if y_val > df['low'][x]:
                # If line intersects the low, check to see if it is a cross or bad line
                if x < x2:
                    # line intersects before reaching the other swing low, its definitely bad
                    bad_line = True
                    break
                if df['close'][x] < y_val:
                    # Trend line is broken by close, signals that trend is good
                    new_point = (x, y_val)
                    break
                if df['close'][x] > y_val:
                    # Trend line intercepts a candle, therefore it should end just before
                    new_point = (x-1, line.get(x-1))

            if not bad_line: trend_lines.append([a, new_point])
    
    # Clean trendlines for any overlap. If (a,b) should be over lapped by the following trend (c,d) where c is before b, make b.x = c.x
        
        
    print(f"{len(trends)} low trends found")
    return trends