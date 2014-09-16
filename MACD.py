from pandas import Series, DataFrame
import pandas as pd
import datetime
#import os.path

#def getDateTime(quotes):
#    quotes['DateTime'] = datetime.datetime.fromtimestamp(quotes.Time).strftime('%Y-%m-%d %H:%M:%S')
    #return time

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
    titles = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose']
    daysAgo = range(0,len(breakLocation)-1)
    
    for day in daysAgo:
        frame = pd.read_csv('daily_AAPL.txt', names = titles)
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
        count = count + 1
        #print quotes.Close.head(10)
        if count >= points:
            Sum  = 0
            for m in range(0,points):
                Sum = Sum + quotes.AdjClose[n - m]
            quotes[s][n] = (Sum / points)
            #print tenSum / 10.0
    return quotes
    
def getMACDSignal(quotes):
    quotes['MACD'] = float('NaN')
    for n in range(26,len(quotes)):
        quotes['MACD'][n] = quotes.MvgAvg12[n] - quotes.MvgAvg26[n]
    return quotes
    
def getMACDTrigger(quotes):
    quotes['MACDTrigger'] = float('NaN')
    for n in range(26,len(quotes)):
        if quotes.MACD[n] > 0:
            quotes.MACDTrigger[n] = 1
        else:
            quotes.MACDTrigger[n] = 0
    return quotes
    
def getBuySell(quotes):
    #Function compares 10 tick average with current price to determine whether to buy.
    #If average is higher than current stock, it is assumed that the stock will increase in value, so buy.
    #!!!Need to add a command to not buy the last stock of the day.  Buying last stock of the day is unpredictable.
    quotes['BuySell'] = float('NaN')
    for n in range(1,len(quotes)):
        if quotes.MvgAvg9[n] != ('NaN'):
            if quotes.MvgAvg9[n] > quotes.AdjClose[n]:
                quotes.BuySell[n] = 1
            else:
                quotes.BuySell[n] = 0
    #for breaks in breakLocation[1:]:
    #    quotes.BuySell[breaks] = 0
        #print breaks
    return quotes
    
def getProfit(quotes):
    #Function calculates profit if stocks were bought.
    #Profits are calculated by comparing stock value when it was bought with the next stock value.
    #Each profit is for the buy command at the same index
    quotes['Profit'] = float('0.0')
    for n in range(1,len(quotes)-1):
        if quotes.BuySell[n] == 1:
            quotes.Profit[n] = quotes.AdjClose[n+1] - quotes.AdjClose[n]
    return quotes

def profitPerDay(quotes):
    return sum(quotes.Profit)
    
def applyStrategy(quotes, bank):
    shares = 0
    for n in range(26,len(quotes)):
        if quotes.MACDTrigger[n] == 1:
            sharesBought = int(bank * 0.5 / quotes.AdjClose[n])
            bankSpent = sharesBought * quotes.AdjClose[n]
            shares = shares + sharesBought
            bank = bank - bankSpent
            if sharesBought:
                print '%s: Bought %d AAPL shares at %.2f per share.  Spent %d.  Bank has %.2f.  Currently %d shares.' % (quotes.Date[n], sharesBought, quotes.AdjClose[n], bankSpent, bank, shares)
        else:
            sell = int(0.5 * shares)
            shares = shares - sell
            sharesSold = sell * quotes.AdjClose[n]
            bank = bank + sharesSold
            if sharesSold:
                print '%s: Sold %d AAPL shares at %.2f per share.  Bank has: %.2f.  Currently %d shares.' % (quotes.Date[n], sell, quotes.AdjClose[n], bank, shares)
        totalBank = bank + (shares * quotes.AdjClose[n])
            
    return totalBank
   
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
    initialInvestment = 50000
    
    #titles = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose']
    readLine = stock+'.txt'
    quotes = pd.read_csv(readLine)
    quotes.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose']
    #print quotes.head()
    
    ##This should be in a function
    #quotes['DateTime'] = '0'
    #for n in range(0,len(quotes)):
    #    quotes.DateTime[n] = datetime.datetime.fromtimestamp(int(quotes.Time[n])).strftime('%Y-%m-%d %H:%M:%S')
    #titles = ['Time', 'DateTime', 'Close', 'High', 'Low', 'Open', 'Volume']
    #quotes = DataFrame(quotes, columns = titles)
    
    #breakLocation = getBreakLocation(quotes['Time'])    #array contains breakpoints
    #blocks = len(breakLocation) - 1  #number of day blocks that we have to work with
    
    #quotes = getDaysAgo(quotes,breakLocation)
    quotes = getMvgAvg(quotes,9)
    quotes = getMvgAvg(quotes,12)       #10 point moving average
    quotes = getMvgAvg(quotes,26)       #15 point moving average  
    quotes = getMACDSignal(quotes)
    quotes = getMACDTrigger(quotes)
    finalInvestment = applyStrategy(quotes,initialInvestment)
    #quotes = getBuySell(quotes)
    #quotes = getProfit(quotes)
    saveFileLine = 'output'+stock+'.txt'
    quotes.to_csv(saveFileLine)
    
    print quotes.tail()
    
    resultsFile = open('outputDailyResults.txt','a')
    
    #totalProfit = quotes.groupby(['DaysAgo']).apply(profitPerDay)
    #print 'Analysis for %s:' % (stock) 
    ##print results
    ##print sum(results)
    
    ##START TEST
    #invested = highestInvestment(quotes,totalProfit)
    #totalProfit.name = 'ProfitPerDay'
    #invested.name = 'HighestInvested'
    #fileOutput = pd.concat([totalProfit,invested], axis = 1)
    #fileOutput['PerformanceInPercentage'] = 100.0 * fileOutput.ProfitPerDay / fileOutput.HighestInvested
    ##END TEST
    
    
    resultsFile.write('\nAnalysis for ' + stock + ':\n')
    #resultsFile.write(str(fileOutput) + '\n')
    #resultsFile.write('Total profits: ' + str(sum(totalProfit)) + '\n')
    #resultsFile.write('Average performance: ' + str(fileOutput.PerformanceInPercentage.mean()) + '\n')
    resultsFile.write('Initial Investment for %s was: %d\n' % (stock, initialInvestment))
    resultsFile.write('Final Investment for %s was: %d\n' % (stock, finalInvestment))
    resultsFile.close()
    
#Main():

#stocksToAnalyze = 'AAPL','GOOG','MSFT','CMG','AMZN','EBAY','TSLA'
#stocksToAnalyze = 'AAPL','ABBV'

createResultsFile = open('outputDailyResults.txt','w')
createResultsFile.close()
for eachStock in stocksToAnalyze:
    stock = 'daily_' + eachStock
    analyzeStock(stock)
