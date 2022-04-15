from DataMiner.import_ticks import *
from pandas.core.frame import DataFrame
from DataMiner.analysis.analyzer import Analyzer
from DataMiner.analysis.strategy import RunStrategy

"""
TO DO: Add Play back and real time chart draw
Add a Way to easily create dataminers from console
"""

class DataMiner:
    """
        Grabs forex and indices data and then runs various analysis, as well as displaying the plot
    """
    def __init__(self, folder= "TradeBoiDeluxe\DataMiner\symbols_data"):
        self.markets = [] # Holds all market data, after candles are built
        self.dates = []
        self.folder = folder
    
    def has_market(self, symbol):
        """
        Check if current market has candle data for given symbol, else return None
        """
        for s, t, c in self.markets:
            if s == symbol: return c, t
        return None

    def set_dates(self, start, end):
        self.dates.append(start)
        self.dates.append(end)
    
    def get_tick_data(self, symbols):
        """
            Saves symbol tick data to folder
        """
        symbols = symbols if isinstance(symbols, list) else [symbols]
        gather(self.dates[0], self.dates[1], symbols, self.folder)
    
    def compile_markets(self, timeframe_minutes, filename=""):
        """
            Read through all of the available symbol data files or a specific file if provided
            and create candles for each with the given timeframe.
        """
        tf_string = f"{timeframe_minutes}Min"
        if filename != "":
            try:
                raw_ticks = get_tick_data(filename)
                candles = ticks_to_candle(raw_ticks, "ask", tf_string)
                candles['volume'] = ticks_to_volume(raw_ticks, tf_string)
                self.markets.append(("XAUUSD", tf_string, candles)) ### Append symbol, candles to market
            except Exception as e:
                print("Unable to compile tick data")
                print(e)
                print(os.curdir)
    
    def candle_save(self):
        """
        Saves each of the markets candle data into csv's, assuming one doesnt exist
        """
        
        os.chdir(self.folder)
        for filename in os.listdir(os.curdir):
            f = os.path.join(os.curdir, filename)
            # checking if it is a file
            if os.path.isfile(f):
                print("Checking for existing candle file in data folder, checking file ", f)
                for sym, timeframe, data in self.markets:
                    if sym in filename and timeframe in filename and data.index[0] in filename and data.index[-1] in filename:
                        print(f"File exists for {sym} {timeframe}, Will not save duplicate file.")
                        continue
                    save_candles(data, sym, timeframe)
        print("All candle data saved.")
    
    def load_all_candles(self):
        """
        Loads all saved candle data
        return last candle data
        """
        os.chdir(self.folder)
        for filename in os.listdir(os.curdir):
            f = os.path.join(os.curdir, filename)
            # checking if it is a file
            if os.path.isfile(f):
                if "candles" not in f:
                    print(f, "is not a candle file.")
                    continue
                try:
                    df = pd.read_csv(f, index_col=0,parse_dates=True)
                    str_arr = filename.split("_")
                    self.markets.append((str_arr[0], str_arr[2],df))
                except Exception as e:
                    print("Failed when trying to load candle file", f, e)
        print("Markets loaded:", [s for s, _, _ in self.markets])

    def load_symbol_candle(self, symbol):
        data = None
        found = False
        for s, _, _ in self.markets:
            if s == symbol:
                print("Candle data exists.")
                found = True
        if not found: return data
        os.chdir(self.folder)
        for filename in os.listdir(os.curdir):
            f = os.path.join(os.curdir, filename)
            # checking if it is a file
            if os.path.isfile(f):
                if "candles" not in f and symbol not in f:
                    print(f, f"is not a {symbol} candle file.")
                    continue
                try:
                    df = pd.read_csv(f, index_col=0,parse_dates=True)
                    str_arr = filename.split("_")
                    data = df
                except Exception as e:
                    print("Failed when trying to load candle file", f, e)
        print("Candle data found for", symbol)
        return data

    def analysis(self, args=[], symbol=""):
        """
        Pass candles of given symbol (or all if left empty), to Analyzer.
        Analyzer will perform various analysis on the DataFrame, and add a new column per analysis.
        Args =
            ('EMA', int period on close), 
            ('Rel_High', int for max high over period eg. 17 or str of time val eg. "240Min")
            ('Rel_Low', int for min low over period eg. 17 or str of time val eg. "240Min")
            ('VWAC', int for period eg. 17 or 0 for day : checks volume per close)
            ('ATR', int for period)
        """
        perform_on_all = symbol == ""
        for s, _, data in self.markets:
            if not perform_on_all and s != symbol: continue
            Analyzer(data, args)

    def clean_data(self, symbol=""):
        """
        Returns a cleaned version of candle data to be run through the strategy simulator.
        EMA columns are changed to short ema and long ema, and ATR is lowercased.
        if no symbol provided, returns the first market.
        """
        if symbol=="":
            _, _, data = self.markets[0]
        emas = []
        for c in data.columns:
            if "EMA" in c:
                ema_arr = c.split(" ")
                emas.append((c, ema_arr[0], int(ema_arr[1])))
            elif "ATR" == c:
                data.rename(columns={c:'atr'},inplace=True)
        print(emas)
        if emas[1][2] < emas[0][2]:
            data.rename(columns={emas[1][0]:'short ema'},inplace=True)
            data.rename(columns={emas[0][0]:'long ema'},inplace=True)
        else:
            data.rename(columns={emas[0][0]:'short ema'},inplace=True)
            data.rename(columns={emas[1][0]:'long ema'},inplace=True)
        data = data.loc[(data!=0).all(1)]
        print("Data cleaned for strategy.")
        print(data.head(3))
        return data
        
    def show(self, symbol, max=2000):
        """
        Show a graph of a given market, assuming market is compiled, with a max number of candles
        """
        market, tf = self.has_market(symbol)
        if len(market) == 0:
            print("No market saved for", symbol, market)
            return
        market = market.truncate(after=market.index[max])
        show(market, tf, symbol)

### Tests
#d = DataMiner()

## for mac
# d = DataMiner(r'TradeBoiDeluxe/DataMiner/symbols_data')
# d.compile_markets(6,".\DataMiner\symbols_data\XAUUSD-2021_04_01-2021_05_01.csv")

## TICK DATA TO CANDLE ON WINDOWS: 
# d.compile_markets(6,"TradeBoiDeluxe/DataMiner/symbols_data/XAUUSD-2021_04_01-2021_05_01.csv")
# SAVE CANDLES: d.candle_save()

## Load all candle data
#d.load_all_candles()

## analysis
# d.analysis([("EMA", 9), ("EMA", 55), ("ATR", 20)])
# d.analysis([("EMA", 9), ("EMA", 55), ("VWAC", 20), ("ATR",20)])
# d.show("XAUUSD", 500)

## Back test strategy
# strat_data = d.clean_data()
# RunStrategy(strat_data,target=2, stop=2,con_rules=['long ema'])



        
        

        
