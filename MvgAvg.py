from pandas import Series, DataFrame
import pandas as pd
import datetime

def getBreakLocation(quotesTime):
    #Function checks the difference between unix Times and determines where a market has closed for the day
    breakLocation = []
    for n in range(1,len(quotesTime)):
        if (quotesTime[n] - quotesTime[n-1]) > 5000:  # current - past
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
        frame = pd.read_csv('stock20Day_AAPL.txt', names = titles)
        frame = quotes[breakLocation[day]+1:(breakLocation[day+1]+1)]
        frame['DaysAgo'] = day
        splitQuotes.append(frame)
        
    quotes = pd.concat(splitQuotes, ignore_index = True)
    return quotes

def getMvgAvg(quotes, points):
    #Function takes the average of points number of ticks.
    s = 'MvgAvg' + str(points)
    quotes[s] = float('NaN')
    count = 1

    for n in range(1,len(quotes)):
        if quotes.DaysAgo[n] != quotes.DaysAgo[n-1]:
            count = 1
            #print "Switch at index = %d" % n
        else:
            count = count + 1
            if count >= points:
                Sum  = 0
                for m in range(0,points):
                    Sum = Sum + quotes.Close[n - m]
                quotes[s][n] = (Sum / points)
                #print tenSum / 10.0
    return quotes
    
def getBuySell(quotes,breakLocation):
    #Function compares 10 tick average with current price to determine whether to buy.
    #If average is higher than current stock, it is assumed that the stock will increase in value, so buy.
    #!!!Need to add a command to not buy the last stock of the day.  Buying last stock of the day is unpredictable.
    quotes['BuySell'] = float('NaN')
    for n in range(1,len(quotes)):
        if quotes.MvgAvg10[n] != ('NaN'):
            if quotes.MvgAvg10[n] > quotes.Close[n]:
                quotes.BuySell[n] = 1
            else:
                quotes.BuySell[n] = 0
    for breaks in breakLocation[1:]:
        quotes.BuySell[breaks] = 0
        #print breaks
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

def profitPerDay(quotes):
    return sum(quotes.Profit)
   
#START TEST 
def highestInvestment(quotes,results):
    grouped = quotes.groupby(['DaysAgo','BuySell'])
    n = []
    for name, group in grouped:
        if name[1] == 1:
            #print group.Close.max()
            #results['Investment'][n] = group.Close.max()
            n.append(group.Close.max())
    #print n
    investmentSeries = Series(n)
    return investmentSeries
#END TEST
    
def analyzeStock(stock):
    titles = ['Time', 'Close', 'High', 'Low', 'Open', 'Volume']
    readLine = 'stock20Day_'+stock+'.txt'
    quotes = pd.read_csv(readLine, names = titles)

    #This should be in a function
    quotes['DateTime'] = '0'
    for n in range(0,len(quotes)):
        quotes.DateTime[n] = datetime.datetime.fromtimestamp(int(quotes.Time[n])).strftime('%Y-%m-%d %H:%M:%S')
    titles = ['Time', 'DateTime', 'Close', 'High', 'Low', 'Open', 'Volume']
    quotes = DataFrame(quotes, columns = titles)
        
    breakLocation = getBreakLocation(quotes['Time'])    #array contains breakpoints
    blocks = len(breakLocation) - 1  #number of day blocks that we have to work with
    
    quotes = getDaysAgo(quotes,breakLocation)
    quotes = getMvgAvg(quotes,10)
    quotes = getBuySell(quotes,breakLocation)
    quotes = getProfit(quotes)
    saveFileLine = 'output_'+stock+'.txt'
    quotes.to_csv(saveFileLine)
    
    resultsFile = open('outputResults_Benchmark.txt','a')
    
    totalProfit = quotes.groupby(['DaysAgo']).apply(profitPerDay)
    print 'Analysis for %s:' % (stock) 
    #print results
    #print sum(results)
    
    #START TEST
    invested = highestInvestment(quotes,totalProfit)
    totalProfit.name = 'ProfitPerDay'
    invested.name = 'HighestInvested'
    fileOutput = pd.concat([totalProfit,invested], axis = 1)
    fileOutput['PerformanceInPercentage'] = 100.0 * fileOutput.ProfitPerDay / fileOutput.HighestInvested
    #END TEST
    
    
    resultsFile.write('\nAnalysis for ' + stock + ':\n')
    resultsFile.write(str(fileOutput) + '\n')
    resultsFile.write('Total profits: ' + str(sum(totalProfit)) + '\n')
    resultsFile.write('Average performance: ' + str(fileOutput.PerformanceInPercentage.mean()) + '\n')
    resultsFile.close()
    
    return fileOutput

stocksToAnalyze = 'AAPL','GOOG','MSFT','CMG','AMZN','EBAY','TSLA'

createResultsFile = open('outputResults_Benchmark.txt','w')
createResultsFile.close()
for eachStock in stocksToAnalyze:
    results = analyzeStock(eachStock)
