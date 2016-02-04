import math

# build the hash with all the necessary keys and arrays as values
def addntoseries(inseries,n):
    inseries['value'].extend([0]*n)
    inseries['point']=list(range(0,len(inseries['value'])))
    inseries['actual_value']=[x for x in inseries['value']]
    inseries['predictions']=[0]*(len(inseries['actual_value']))
    inseries['expected_value']=[0]*(len(inseries['actual_value']))
    return inseries

# run the forecast module...identical to arima forecast module
def forecast(series,n):
    start=len(series['value'])
    outseries=runmadforecast(series,n)
    return {'value':outseries['value'][start:],'point':outseries['point'][start:],'actual_value':outseries['actual_value'][start:],'predictions':outseries['predictions'][start:],'expected_value':outseries['expected_value'][start:]}

# run the history module...identical to arima history module
def history(series,n):
    return runmadforecast(series,n,lastonly=False)

# get median of a list
def median(lst): return sorted(lst)[len(lst)//2]

# get median absolute deviation of a list
def meddev(lst): 
    med=median(lst)
    mads=[]
    for b in lst: mads.append(math.fabs(b-med))
    return median(mads)

# run MAD forecast
# seriesin is the series hash {point,value} as keys
# n is the number of days to be predicted
# lastonly will only run on the last 0 to n points thus only doing the forecast portion
# minrequired is the number of points required in the series
# lookback is the moving lookback window in terms of points
# mult is the multiple to apply to the MAD
def runmadforecast(seriesin,n,lastonly=True,minrequired=4,lookback=10,mult=7):
    inseries=addntoseries(seriesin,n)
    if len(inseries['value'])<minrequired: return inseries
    vals=[x for x in inseries['value']]
    if lastonly: rangeset=range(len(vals)-n,len(vals)) #run only on the new points in the series 
    else: rangeset=range(minrequired,len(vals)) #run only on the points from minrequired to end of series
    for i in rangeset:
        totalset=vals[max(0,i-lookback):i] #ensure not trying to pull negative indexed values from list
        mad=meddev(totalset)
        med=median(totalset)
        upper=med+mult*mad
        lower=med-mult*mad
        inseries['expected_value'][i]=med
        inseries['predictions'][i]=(lower,upper)
        vals[i]=med #naturally the median will stagnate as n increases. mad will also decrease eventually down to 0 as n increases
        # print "i %s totalset %s mad %s med %s upper %s lower %s inseries %s" %(i,totalset,mad,med,upper,lower,inseries)
    return inseries

#inputvalues=[float(x) for x in range(1,3)]
#inputpoints=list(range(0,len(inputvalues)))
#input_series={'point': inputpoints, 'value':inputvalues}
#print forecast(input_series,1)
