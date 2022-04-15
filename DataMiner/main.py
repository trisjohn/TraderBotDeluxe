"""
Terminal Program that allows creating new data miners, running back tests, and showing historical and live candle data
"""
import datetime
VERSION = 0.01
def show_menu():
    print(
        f"""
        --[DataMiner Version {VERSION}]--

        Set     Download  Save
        Compile Run Show  Quit

        'help' to show command prefix
        'list' to show all commands
        """
    )

def get_input(prefix = "> ", typ = str):
    """
    Return the input of the user, force a certain type given the typ variable
    """
    try:
        val = typ(input(prefix))
    except Exception as e:
        print("Unable to fix type to input", e)
    return val

def show_basic():
    """
    Show the basic commands
    """ 
    print(
        """
        -s [Attribute Set]
        -g [Attribute Get]
        -d [Get Raw data]
        -m [MenuFileName]
        -compile [Raw to Candles]
        -r [Backtest]
        -show [Historical Chart]
        -live [Live Chart]
        -exit -end -q -quit
        """
    )

def list_all():
    print(
        """
        Set/Get [Attribute]: -s/-g
            (symbol: sym, symb)/(start_date): startdate 1date 1stdate sdate)/(end_date: enddate 2date 2nddate edate)/(timeframe: tf, timef, tframe, timeframe)
            (folder: folder, dest, fold)
            -g all (to display all attributes)

        Download [Must have symbol, folder, start and end data set]: -d
        Save [current attributes to a new menu] -m menuname
        Help [Specific command] -h (r/s/compile)
        Compile [Compile tick data into candles, time frame must be set] -compile
        Run [Backtest a strategy] -r params:[]
        Show [Show candle/analysis] -show (for historical data of the given attributes) -live (for live data of the given symbol and timeframe)
        Quit: [end program] -exit -end -q -quit
        """
    )

def work_choice(choice):
    """
    Check choice to see what further information is needed if not already given
    """
    arr = choice.split(" ")
    print(arr)
    if arr[0] == '-q' or arr[0] == '-quit' or arr[0] == '-exit' or arr[0] == '-end' or arr[0] == 'quit': return False
    
    return True

def main():
    """
    Menu:
        Set [Attribute]: -s 
            (symbol: sym, symb)/(start_date): startdate 1date 1stdate sdate)/(end_date: enddate 2date 2nddate edate)/(timeframe: tf, timef, tframe, timeframe)
            (folder: folder, dest, fold)
        Download [Must have symbol, folder, start and end data set]: -d
        Save [current attributes to a new menu] -m menuname
        Help [Expands full command list]
        Compile [Compile tick data into candles, time frame must be set] -compile
        Run [Backtest a strategy] -r params:[]
        Show [Show candle/analysis] -show (for historical data of the given attributes) -live (for live data of the given symbol and timeframe)
        Quit: [end program] -exit -end -q -quit

    """
    session_start = datetime.datetime.now()
    # Print Menu
    show_menu()
    while True:
        current_time = datetime.datetime.now()
        print(f"[{current_time}]")
        choice = get_input()
        print(choice)
    # Check choice
        if(choice == 'help'): show_basic()
        elif(choice == 'list'): list_all()
        else:
            if not work_choice(choice): break
    
    # Summary of what was accomplished
    print(
        f"""
            Your session time: {current_time - session_start}
        """
    )

main() 