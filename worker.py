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
callsPerDay = 48 # This should be determined by the frequency of calls (defined in bot.py)
                 # If called every 30 minutes, there are 48 calls per day
                 # Can tweak this if not seeking to remove a ticker from consideration for a full day

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

# Returns true if alert triggered, false if not
    # Considers the candle before the current one (second to last element of volumes)
    # Calculates the mean of the candles prior to the considered candle
    # Calculates the maximum of the candles prior to the considered candle
    # Returns a boolean:
    #   True if the considered candle is > (multiplier * mean) AND candle is > max
    #   False if not
def determineAlert(symbol, volumes):
    global cooldownList
    global cooldownTimes
    numCandles = len(volumes)
    considered = volumes[numCandles-2]
    mean = np.mean(volumes[:numCandles-2])
    max = np.max(volumes[:numCandles-2])
    # print("comparing " + str(volumes[numCandles-2]) + " to " + str((multiplier * mean)) + " and max " + str(max)) # Testing
    if((considered > (multiplier * mean)) and (considered > max)):
        cooldownList.append(symbol)
        cooldownTimes.append(0)
        return True
    else:
        return False


#================================================ PRODUCTION ================================================

# Pull volumes and look for spikes
# Returns None if no spikes OR a list of strings if there are spikes
def detect():
    isReturning = False
    alerts = []
    updateCooldown()
    activeList = excludeCooldown(tokenList)
    print("Running check...")
    for x in activeList:
        symbol = x
        volumes = getVolArray(exch, x, timeframe)
        # print(symbol) # Testing
        # pprint(volumes) # Testing
        alert = determineAlert(symbol, volumes)
        if(alert):
            isReturning = True
            alerts.append("Volume spike detected on " + x)
    if(isReturning):
        return alerts
    else:
        print('None found (volume)')
        return None
