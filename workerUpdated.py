import ccxt
from pprint import pprint
import time
import datetime
import numpy as np

# Documentation here: https://github.com/ccxt/ccxt
# and here: https://docs.ccxt.com/en/latest/manual.html


#================================================ VARIABLES ================================================

# List of tickers - must conform to the API's requirements
# This list works with Binance
tokenList = ['FTM/USDT', 'AVAX/USDT', 'NEAR/USDT', 'RUNE/USDT', 'DOT/USDT', 'AXS/USDT', 'ENJ/USDT', 'LINK/USDT',
            'MATIC/USDT', 'FTT/BUSD', 'SRM/USDT', 'MKR/USDT', 'XTZ/USDT', 'ATOM/USDT', 'CHZ/USDT', 'ALGO/USDT',
            '1INCH/USDT', 'MANA/USDT', 'LRC/USDT', 'YFI/USDT', 'GRT/USDT', 'SNX/USDT', 'SUSHI/USDT', 'LUNA/USDT',
            'SOL/USDT']

# What timeframe to use for candles
timeframe = '30m'

# How many hours to consider when pulling data
lookbackHours = 24

# A spike is reported if
#   (a) the most recent full candle is > (multiplier * mean of all other candles in the timeframe), AND
#   (b) most recent full candle is > maximum volume found over all other candles in the timeframe
# Can tweak this in determineAlert function
multiplier = 3.3

# Exchange to use. Check documentation for others available
# As stated above, tokenList must be compatible with how the exchange accepts calls
# If changing the exchange, may need to do test calls to see what format the exchange accepts tickers for
# ** Need to add dex support **
exch = ccxt.binance({'rateLimit': 100})


#================================================ COOLDOWN ================================================

# Allows tickers to be, once an alert is triggered, ignored for a certain time period
# Tickers that are in this 'cooldown period' are stored in cooldownList

# Using a day-long cooldown on alerts for each token
cooldownList = []
cooldownTimes = []
callsPerDay = 8  # This should be determined by the frequency of calls (defined in bot.py)
                 # If called every 30 minutes, there are 48 calls per day
                 # Can tweak this if not seeking to remove a ticker from consideration for a full day
                 # Note: Moving this lower, only want removal for a few cycles

maxAlerts = 2 # Number of alerts that can be sent out at once (for prioritization/readability)

# Increases cooldown or puts it back into circulation if the day is up
def updateCooldown():
    global cooldownList
    global cooldownTimes
    deleteIndices = []
    for idx, x in enumerate(cooldownTimes):
        if(x >= callsPerDay):
            deleteIndices.append(idx)
        else:
            cooldownTimes[idx] += 1
    for x in sorted(deleteIndices, reverse=True):
        del cooldownList[x]
        del cooldownTimes[x]

# Returns a list of tokens not on the cooldown list
def excludeCooldown(list):
    return [x for x in list if x not in cooldownList]


#================================================ HELPERS ================================================

# Returns a numpy.ndarray of volumes using the specified timeframe and hours to use for history
def getVolArray(exchange, symbol, timeframe):
    exchange.options['defaultType'] = 'future' # looking at perps
    exchange.load_markets()

    startTime = datetime.datetime.now() - datetime.timedelta(hours=lookbackHours)
    unixTime = time.mktime(startTime.timetuple()) * 1000

    ohlcv = np.array(exchange.fetch_ohlcv(symbol, timeframe, unixTime))
    return ohlcv[:,5]

# Takes a list of symbols and a list of numpy arrays and returns the most relevant (up to 3) volume spike alerts
def determineAlerts(symbols, volumes):
    global cooldownList
    global cooldownTimes
    numCandles = len(volumes[0]) # all volumes should have same length
    spikeSymbols = [] # store all symbols we find spikes for
    magnitudes = [] # quantify the magnitude of each spike for the sake of comparison
    results = [] # will store alert strings
    iterator = 0 # don't want to use enumerate rn
    for volArr in volumes:
        considered = volArr[numCandles-2]
        mean = np.mean(volArr[:numCandles-2])
        max = np.max(volArr[:numCandles-2])
        if((considered > (multiplier * mean)) and (considered > max)):
            # we have found a spike
            print("Spike found on " + symbols[iterator])
            spikeSymbols.append(symbols[iterator])
            magnitudes.append((abs(considered - (multiplier * mean)) / (multiplier * mean)) * 100.0) # % difference
        iterator += 1
    if(len(spikeSymbols) == 0):
        return results
    elif(len(spikeSymbols) <= maxAlerts):
        # create output array and return it
        for x in spikeSymbols:
            results.append("Volume spike detected on " + x)
            cooldownList.append(x)
            cooldownTimes.append(0)
        return results
    else:
        # only return top 2 spikes
        magsToSymbols = dict(zip(magnitudes, spikeSymbols))
        iterator2 = 0
        for x in sorted(magnitudes, reverse=True):
            results.append("Volume spike detected on " + magsToSymbols[x])
            cooldownList.append(magsToSymbols[x])
            cooldownTimes.append(0)
            if(iterator2 == (maxAlerts - 1)):
                return results
            iterator2 += 1



#================================================ PRODUCTION ================================================

# Pull volumes and look for spikes
# Returns None if no spikes OR a list of strings if there are spikes
def detect():
    isReturning = False
    alerts = []
    updateCooldown()
    activeList = excludeCooldown(tokenList)
    print("Running check...")
    print("Cooldown list is now (see below)")
    print(cooldownList)
    volumes = []
    for x in activeList:
        symbol = x
        volumes.append(getVolArray(exch, x, timeframe))
        print(symbol) # Testing
    pprint(volumes) # Testing
    alerts = determineAlerts(activeList, volumes)
    if(len(alerts) > 0):
        return alerts
    else:
        print('None found (volume)')
        return None
