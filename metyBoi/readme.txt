Version 0.1 of mety boi

XXXX TO DO XXXX

1. Trade Options should be appended when saved
    a. On update, read through trade options to see if market conditions allow trade entry
    b. Delete any trade options whose rrequirements were met and a market order was made
    c. Save resulting market order as pending. (see Market orders)

2. Market Orders must be added as their own class and data file
    a. On update, read through market orders and test against server if they have been filled.
    b. Cancel all market orders past expiration
    c. Build Positions for all successful market orders (see Position)
    d. Collect and save historical data on successful market order fill (see Entry Data)

3. Build position class and data file
    a. On update, calculate and update position trail stop (modify position and virtual stop), check for take profit hit 
    b. If take profit hit, flag position and update break even, then on update, check for exit via exit_signal or virtual stop trigger