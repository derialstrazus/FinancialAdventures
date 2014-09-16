# S&P100.txt contains list of S&P100 companies.  Just copy paste from wikipedia into a text file.

import urllib2
import time
import datetime
import os.path
#import os.getcwd

SnP100File = 'S&P100.txt'
SnPData = open(SnP100File,'r').read()
splitSnPData = SnPData.split('\n')

stocksToPull = []
for eachLine in splitSnPData:
    splitLine = eachLine.split('\t')
    stocksToPull.append(splitLine[0])
    
print stocksToPull
# stocksToPull = 'AAPL','GOOG','MSFT','CMG','AMZN','EBAY','TSLA','EURUSD=X','USDEUR=X'



def pullData(stock):
    try:
        print 'Currently pulling',stock
        print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        urlToVisit = 'http://real-chart.finance.yahoo.com/table.csv?s='+stock+'&d=8&e=13&f=2014&g=d&a=11&b=12&c=2000&ignore=.csv'
        # urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=20d/csv'

        saveDir = os.getcwd()+'\SnP100Daily'        
        fileName = 'raw_daily_'+stock+'.txt'
        filePath = os.path.join(saveDir, fileName)
                
        saveFile = open(filePath,'w')
        sourceCode = urllib2.urlopen(urlToVisit).read()        

        saveFile.write(sourceCode)
        saveFile.close()
                        
        print 'Pulled',stock
        #print 'sleeping.....'
        #print str(datetime.datetime.fromtimestamp(time.time()).strftime('%Yos-%m-%d %H:%M:%S'))
                
    except Exception,e:
        print 'main loop', str(e)

for eachStock in stocksToPull: 
    pullData(eachStock)
