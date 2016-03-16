import math,copy,sys,datetime
from statsmodels.tsa.arima_model import ARIMA
from multiprocessing import Pool

# build the hash with all the necessary keys and arrays as values
def addntoseries(inseries,n,ensemble=False):
    inseries['value'].extend([0]*n)
    inseries['point']=list(range(0,len(inseries['value'])))
    inseries['actual_value']=[x for x in inseries['value']]
    if ensemble: inseries['ensemble']=[0]*(len(inseries['actual_value']))
    else: 
        inseries['predictions']=[0]*(len(inseries['actual_value']))
        inseries['expected_value']=[0]*(len(inseries['actual_value']))
    return inseries

###############################################################################
# ARIMA FUNCTIONS
###############################################################################
# determine if the value is NaN
def isNaN(x): return str(float(x)).lower() == 'nan'

# returns the aic of an arima model
def arima_aic(values,order):
    #fit=ARIMA(values, order=order).fit(method='mle',disp=False,skip_hessian=True,full_output=False)
    fit=ARIMA(values, order=order).fit(method='mle',disp = False, warn_convergence = False)
    return fit.aic

def ijk_worker((i,j,k)):
    taics={}
    if len(gvals)>(i+j+k):
        try:
            aic=arima_aic(gvals,(i,j,k))
            taics[(i,j,k)]=aic
        except: taics[(i,j,k)]=0
    else: taics[(i,j,k)]=0
    return taics

# run the auto arima portion and then return the EV and CI of the lowest AIC model
def autoarima(vals,n=1,confidence_interval_alpha=.01):
    lenval=len(vals)
    global gvals
    gvals=vals
    #print('autoarima')
    aics={}
#    for i in [0,1,2]:
#        for j in [0,1]:
#            for k in [0,1,2]:
#                if(len(vals)>(i+j+k)):
#                    try:
#                        aic=arima_aic(vals,(i,j,k))
#                        #print(' '.join(['i','j','k','aic']))
#                        #print(' '.join(str([i,j,k,aic])))
#                        aics[(i,j,k)]=aic
#                    except:
#                        pass
    ijks=[(i,j,k) for i in [0,1,2] for j in [0,1] for k in [0,1,2]]
    poolsize=20
    myPool=Pool(poolsize)
    myresults=myPool.map(ijk_worker,ijks)
    myPool.close()
    first=True
    for i in range(0,len(myresults)):
        (aics)=myresults[i]
        # get the bestkey
        for key in aics.keys():
            val=aics[key]
            if (not (isNaN(val))) and (val!=0):
                if first:
                    bestaic=val
                    bestkey=key
                    first=False
                else:
                    if val<bestaic:
                        bestaic=val
                        bestkey=key
                #print(str(key)+' '+str(val))


    if first:
        #print('no best aic found')
        bestkey=(0,0,0)
    try: 
	model=ARIMA(vals, order=bestkey).fit(method='mle',disp = False, warn_convergence = False)
        i=bestkey[0]
        j=bestkey[1]
        k=bestkey[2]
	#print "%s (%s,%s,%s)" %(lenval,i,j,k)
    except: 
	model=ARIMA(vals, order=(0,0,0)).fit(method='mle',disp = False, warn_convergence = False)
	#print "%s (0,0,0)" %lenval
    predict_model=model.forecast(n,alpha=confidence_interval_alpha)
    expected_value=predict_model[0].tolist()
    confidence_intervals=predict_model[2:len(predict_model)][0].tolist()
    return (expected_value,confidence_intervals)

# run the arima forecast used in both the forecast and history functions
# seriesin is the series hash {point,value} as keys
# n is the number of days to be predicted
# lastonly will only run on the last 0 to n points thus only doing the forecast portion
# minrequired is the number of points required in the series
# lookback is the moving lookback window in terms of points
def runarimaforecast(seriesin,n,lastonly=True,minrequired=4,lookback=21):
    inseries=addntoseries(seriesin,n)
    if len(inseries['value'])<minrequired: return inseries
    vals=[x for x in inseries['value']]
    if lastonly: rangeset=range(len(vals)-n,len(vals)) #run only on the new points in the series 
    else: rangeset=range(minrequired,len(vals)) #run only on the points from minrequired to end of series
    for i in rangeset:
        totalset=vals[max(0,i-lookback):i] #ensure not trying to pull negative indexed values from list
        (expected_value,confidence_interval)=autoarima(totalset)
        #print 'finished %s %s' %(i,datetime.datetime.now())
        inseries['expected_value'][i]=expected_value[0]
        inseries['predictions'][i]=confidence_interval[0]
        if lastonly: vals[i]=expected_value
    outseries=copy.deepcopy(inseries)
    return outseries

###############################################################################
# MAD/IQR FUNCTIONS
###############################################################################
# get median of a list
def median(lst): return sorted(lst)[len(lst)//2]

# get median absolute deviation of a list
def meddev(lst): 
    med=median(lst)
    mads=[]
    for b in lst: mads.append(math.fabs(b-med))
    return median(mads)

# get the percentile of a list
def percentile(lst,percent):
    i=int(round(percent*len(lst)+.5))
    return sorted(lst)[i-1]

# run the MAD forecast used in both the forecast and history functions
# seriesin is the series hash {point,value} as keys
# n is the number of days to be predicted
# lastonly will only run on the last 0 to n points thus only doing the forecast portion
# minrequired is the number of points required in the series
# lookback is the moving lookback window in terms of points
# mult is the multiple to apply to the MAD
def runmadforecast(seriesin,n,lastonly=True,minrequired=4,lookback=10,mult=7):
    #print 'lookback %s mult %s'%(lookback,mult)
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
        if lastonly: vals[i]=med #naturally the median will stagnate as n increases. mad will also decrease eventually down to 0 as n increases
        # print "i %s totalset %s mad %s med %s upper %s lower %s inseries %s" %(i,totalset,mad,med,upper,lower,inseries)
    outseries=copy.deepcopy(inseries)
    return outseries

# run the IQR forecast used in both the forecast and history functions
# seriesin is the series hash {point,value} as keys
# n is the number of days to be predicted
# lastonly will only run on the last 0 to n points thus only doing the forecast portion
# minrequired is the number of points required in the series
# lookback is the moving lookback window in terms of points
# mult is the multiple to apply to the MAD
def runiqrforecast(seriesin,n,lastonly=True,minrequired=4,lookback=10,mult=3):
    inseries=addntoseries(seriesin,n)
    if len(inseries['value'])<minrequired: return inseries
    vals=[x for x in inseries['value']]
    if lastonly: rangeset=range(len(vals)-n,len(vals)) #run only on the new points in the series 
    else: rangeset=range(minrequired,len(vals)) #run only on the points from minrequired to end of series
    for i in rangeset:
        totalset=vals[max(0,i-lookback):i] #ensure not trying to pull negative indexed values from list
        med=median(totalset)
        iqr=percentile(totalset,.75)-percentile(totalset,.25)
        upper=med+mult*iqr
        lower=med-mult*iqr
        inseries['expected_value'][i]=med
        inseries['predictions'][i]=(lower,upper)
        if lastonly: vals[i]=med #naturally the median will stagnate as n increases. mad will also decrease eventually down to 0 as n increases
        # print "i %s totalset %s mad %s med %s upper %s lower %s inseries %s" %(i,totalset,mad,med,upper,lower,inseries)
    outseries=copy.deepcopy(inseries)
    return outseries

###############################################################################
# Ensemble FUNCTIONS
###############################################################################
def runensembleforecast(seriesin,n,lastonly=True,minrequired=4):
    inseries=addntoseries(seriesin,n,ensemble=True)
    if len(inseries['value'])<minrequired: return inseries
    vals=[x for x in inseries['value']]
    if lastonly: rangeset=range(len(vals)-n,len(vals)) #run only on the new points in the series
    else: rangeset=range(minrequired,len(vals)) #run only on the points from minrequired to end of series

    madresults77=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=7)
    madresults714=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=7)
    madresults721=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=7)
    madresults67=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=6)
    madresults614=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=6)
    madresults621=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=6)
    madresults87=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=8)
    madresults814=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=8)
    madresults821=runmadforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=8)

    iqrresults37=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=3)
    iqrresults314=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=3)
    iqrresults321=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=3)
    iqrresults27=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=2)
    iqrresults214=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=2)
    iqrresults221=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=2)
    iqrresults47=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7,mult=4)
    iqrresults414=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=14,mult=4)
    iqrresults421=runiqrforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21,mult=4)

    arimaresults7=runarimaforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=7)
    arimaresults21=runarimaforecast(seriesin,n,lastonly=lastonly,minrequired=minrequired,lookback=21)

    for ii in rangeset:
        val=vals[ii]
        preds=[]
        results=['iqrresults','madresults','arimaresults']
        for result in results:
            if result=='madresults': resultadds=[str(i)+str(j) for i in [6,7,8] for j in [7,14,21]]
            if result=='iqrresults': resultadds=[str(i)+str(j) for i in [2,3,4] for j in [7,14,21]]
            if result=='arimaresults': resultadds=[str(i) for i in [7,21]]
            weight=(1.0/len(results))/len(resultadds)
            for resultadd in resultadds:
                resultname=result+resultadd
                low,high=eval(resultname+'["predictions"][ii]')
                if val>=low and val<=high: pred=0.0 #not an anomaly
                else: pred=weight
                #print 'ii %s resultname %s val %s low %s high %s pred %s' %(ii,resultname,val,low,high,pred)
                preds.append(pred)
        pct=sum(preds)
        if pct>(1.0/len(results)): inseries['ensemble'][ii]=1
#	madlow, madhigh = madresults["predictions"][i]
#        iqrlow, iqrhigh = iqrresults["predictions"][i]
#        arimalow, arimahigh = arimaresults["predictions"][i]
#        if val>=madlow and val<=madhigh: madpred=0 #not an anomaly
#        else: madpred=1
#        if val>=iqrlow and val<=iqrhigh: iqrpred=0 #not an anomaly
#        else: iqrpred=1
#        if val>=arimalow and val<=arimahigh: arimapred=0 #not an anomaly
#        else: arimapred=1
#        if (madpred+iqrpred+arimapred)/3 >=.5: inseries['ensemble'][i]=1

    return inseries
        
        

###############################################################################
# Running FUNCTIONS
###############################################################################
# run the forecast module
def forecast(series,n):
    start=len(series['value'])
    outseries=runmadforecast(series,n)
    return {'value':outseries['value'][start:],'point':outseries['point'][start:],'actual_value':outseries['actual_value'][start:],'predictions':outseries['predictions'][start:],'expected_value':outseries['expected_value'][start:]}

# run the history module
def history(series,n):
    return runensembleforecast(series,n,lastonly=False)



