import pandas as pd

def getBreakLocation(quotesTime):
    #Function checks the difference between unix Times and determines where a market has closed for the day
    breakLocation = []
    for n in range(1,len(quotesTime)):
        if (quotesTime[n] - quotesTime[n-1]) > 1000:  # current - past
            breakLocation.append(n-1)
            # print 'break at location ' + str(n-1) + ' and time: ' + str(quotesTime[n-1])
    breakLocation = [-1] + breakLocation + [len(quotesTime) - 1]    #array goes from -1 to end of quote, 12 numbers for 11 blocks
    return breakLocation

def getDaysAgo(quotes,breakLocation):
    #Function uses breakLocation to label each index to a certain date, splitting the time series into separate days
    splitQuotes = []
    titles = ['Time', 'Close', 'High', 'Low', 'Open', 'Volume']
    daysAgo = range(0,len(breakLocation)-1)
    
    for day in daysAgo:
        frame = pd.read_csv('AAPL.txt', names = titles)
        frame = quotes[breakLocation[day]+1:(breakLocation[day+1]+1)]
        frame['DaysAgo'] = day
        splitQuotes.append(frame)
        
    quotes = pd.concat(splitQuotes, ignore_index = True)
    return quotes

def getTenDayAvg(quotes):
    #Function takes the average of 10 ticks.
    quotes['TenDayAvg'] = float('NaN')
    tenCount = 1

    for n in range(1,len(quotes)):
        if quotes.DaysAgo[n] != quotes.DaysAgo[n-1]:
            tenCount = 1
            #print "Switch at index = %d" % n
        else:
            tenCount = tenCount + 1
            if tenCount >= 10:
                tenSum  = 0
                for m in range(0,10):
                    tenSum = tenSum + quotes.Close[n - m]
                quotes.TenDayAvg[n] = (tenSum / 10.0)
                #print tenSum / 10.0
    return quotes
    
def getBuySell(quotes,breakLocation):
    #Function compares 10 tick average with current price to determine whether to buy.
    #If average is higher than current stock, it is assumed that the stock will increase in value, so buy.
    #!!!Need to add a command to not buy the last stock of the day.  Buying last stock of the day is unpredictable.
    quotes['BuySell'] = float('NaN')
    for n in range(1,len(quotes)):
        if quotes.TenDayAvg[n] != ('NaN'):
            if quotes.TenDayAvg[n] > quotes.Close[n]:
                quotes.BuySell[n] = 1
            else:
                quotes.BuySell[n] = 0
    for breaks in breakLocation[1:]:
        quotes.BuySell[breaks] = 0
        print breaks
    return quotes
    
def getProfit(quotes):
    #Function calculates profit if stocks were bought.
    #Profits are calculated by comparing stock value when it was bought with the next stock value.
    #Each profit is for the buy command at the same index
    quotes['Profit'] = float('0.0')
    for n in range(1,len(quotes)-1):
        if quotes.BuySell[n] == 1:
            quotes.Profit[n] = quotes.Close[n+1] - quotes.Close[n]
    return quotes

def resultsPerDay(quotes):
    return sum(quotes.Profit)
    
def analyzeStock(stock):
    titles = ['Time', 'Close', 'High', 'Low', 'Open', 'Volume']
    readLine = 'stock20Day_'+stock+'.txt'
    quotes = pd.read_csv(readLine, names = titles)
    
    breakLocation = getBreakLocation(quotes['Time'])    #array contains breakpoints
    blocks = len(breakLocation) - 1  #number of day blocks that we have to work with
    
    quotes = getDaysAgo(quotes,breakLocation)
    quotes = getTenDayAvg(quotes)
    quotes = getBuySell(quotes,breakLocation)
    quotes = getProfit(quotes)
    saveFileLine = 'output_'+stock+'.txt'
    quotes.to_csv(saveFileLine)
    
    resultsFile = open('outputResults.txt','a')
    
    results = quotes.groupby(['DaysAgo']).apply(resultsPerDay)
    print 'Analysis for %s:' % (stock) 
    print results
    print sum(results)
    
    resultsFile.write('\nAnalysis for ' + stock + ':\n')
    resultsFile.write(str(results) + '\n')
    resultsFile.write('Total profits: ' + str(sum(results)) + '\n')
    resultsFile.close()

stocksToAnalyze = 'AAPL','GOOG','MSFT','CMG','AMZN','EBAY','TSLA'

createResultsFile = open('outputResults.txt','w')
createResultsFile.close()
for eachStock in stocksToAnalyze:
    analyzeStock(eachStock)
