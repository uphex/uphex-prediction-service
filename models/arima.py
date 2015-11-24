import copy
import datetime
import sys

from statsmodels.tsa.arima_model import ARIMA

def forecast(series,n):
    series = timeseriestoseries(series)
    series = runarimaforecast(series,n)
    nseries = fill_series(series,i=(len(series['point'])-n))
    nseries['expected_value'] = copy.deepcopy(nseries['value'])
    prediction = keystoreturn(nseries,('expected_value','actual_value','predictions','point'))

    #print('final forecast series')
    #print(prediction)

    return prediction

def keystoreturn(ser,keys):
    tobereturned = {}

    for key in ser.iterkeys():
        if key in keys:
            tobereturned[key]=copy.deepcopy(ser[key])

    return tobereturned


def runforecast(series,n,minrequired=4,lookback=2):
    start = len(series['point'])
    #print series

    if len(series['point'])<minrequired:
        return series

    for i in range(start,start+n):
        temp=series['value'][max(i-lookback,0):i]
        #print temp
        series['point'].append(max(series['point'][(i-1):])+1)
        series['value'].append(float(sum(temp))/len(temp))

    return series

def appendelements(series,appendseries):
    for key in appendseries.iterkeys():
        t=appendseries[key]

        if len(t)>0:
            tt=max(t)
        else:
            tt=None

        if key not in series.iterkeys():
            series[key]=[]

        series[key].append(tt)

    return series

def history(series,n):
    series=timeseriestoseries(series)
    #print('history function series')
    #print(series)
    returnelements={}
    for i in range(0,(len(series['point'])+n)):
        series2=fill_series(series,j=i)
        #print("history series2")
        #print(series2)
        elements=runarimaforecast(series2,n)
        #print("history elements")
        #print(elements)
        #temp_predictions=elements['value']
        elements=fill_series(elements,i=i,j=(i+1))
        elements['actual_value']=series['value'][i:(i+1)]
        #elements['predictions'].append(temp_predictions)
        #print("history elements")
        #print(elements)
        elements['expected_value']=elements['value']
        returnelements=appendelements(returnelements,elements)
    prediction=keystoreturn(returnelements,('expected_value','actual_value','predictions','point'))
    #print('history prediction')
    #print(prediction)
    return prediction


def fill_series(ser,i=None,j=None):
    ser2={}

    for key in ser.iterkeys():
        ser2[key]=ser[key][i:j]

    return ser2




def arima_aic(values,order):
    #fit=ARIMA(values, order=order).fit(method='mle',disp=False,skip_hessian=True,full_output=False)
    fit=ARIMA(values, order=order).fit(method='mle',disp = False, warn_convergence = False)
    return fit.aic

def autoarima(y):
    #print('autoarima')
    aics={}
    for i in [0,1,2]:
        for j in [0,1]:
            for k in [0,1,2]:
                if(len(y)>(i+j+k)):
                    try:
                        aic=arima_aic(y,(i,j,k))
                        #print(' '.join(['i','j','k','aic']))
                        #print(' '.join(str([i,j,k,aic])))
                        aics[(i,j,k)]=aic
                    except:
                        pass
    first=True
    for key in aics.iterkeys():
        val=aics[key]
        if not (isNaN(val)):
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
        return (0,0,0)
    else:
        #print('bestaic '+str(bestaic)+' bestkey '+str(bestkey))
        return bestkey

def runarimaforecast(series,n,minrequired=4,lookback=21,confidence_interval_alpha=.01):
    if len(series['value'])<minrequired:
        return series
    #print("series")
    #print(series)
    vals=series['value']
    j=len(vals)
    i=max(j-lookback,0)
    bestkey=autoarima(vals[i:j])
    #print("bestkey")
    #print(bestkey)
    if(bestkey!=0):
        maxpoint=max(series['point'])
		try: 
			model=ARIMA(series['value'], order=bestkey).fit(method='mle',disp = False, warn_convergence = False)
		except: 
			model=ARIMA(series['value'], order=(0,0,0)).fit(method='mle',disp = False, warn_convergence = False)
        predict_model=model.forecast(n,alpha=confidence_interval_alpha)
        confidence_intervals=predict_model[2:len(predict_model)][0]
        #print('confidence_intervals')
        #print(confidence_intervals)

        series['predictions'].extend(confidence_intervals.tolist())
        #print('\npredict')
        #print(predict_model[0])
        series['point'].extend(range((maxpoint+1),(maxpoint+n+1)))
        series['value'].extend(predict_model[0].tolist())
    #print('series')
    #print(series)
    return series

def isNaN(x):
    return str(float(x)).lower() == 'nan'

def timeseriestoseries(ts):
    ts2={}
    ts2['value']=ts['value']
    ts2['point']=ts['point']
    ts2['actual_value']=copy.deepcopy(ts['value'])
    ts2['predictions']=[0]*(len(ts2['actual_value']))
    ts2['expected_value']=[0]*(len(ts2['actual_value']))
    return ts2

def readTextFile(metric,filename="observations.csv"):
    header=False
    dirfilename=dir+"/"+filename
    d=[]
    with open(dirfilename,'rb') as source:
        for line in source:
            if header:
                fields=line.rstrip().split(',')
                fields[1]=datetime.datetime.strptime(fields[1][0:19],"%Y-%m-%d %H:%M:%S")
                if int(fields[4])==metric:
                    d.append(float(fields[2]))

            header=True
    #print d
    return d
