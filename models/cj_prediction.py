import ensemble,sys

vals=[]
#N=713
with open('SYB-sessions.csv.head','r') as f:
    header=True
#    filelines=[f.readline() for i in range(N)]
#    filelines=f.readlines()
    for line in [l for l in (ll.strip() for ll in f.readlines()) if l]:
        if header: header=False
        else: 
            lines=line.split(',')
            #print lines
            vals.append(lines[1])

#input_values = [float(x) for x in [44.0,56.0,34.0,46.0,33.0,50.0,43.0,46.0,32.0,31.0,24.0,43.0,53.0,44.0,33.0,39.0,44.0,34.0,50.0,46.0,74.0,57.0,45.0,52.0,49.0,47.0,44.0,27.0,32.0,49.0,27.0,30.0,29.0,33.0,30.0,25.0,28.0,32.0,30.0,32.0,31.0,36.0,27.0,52.0,2900.0]]
vals.reverse()
input_values = [float(x) for x in vals]
input_points = list(range(0, len(input_values)))
input_series = {"point": input_points, "value": input_values}
result=ensemble.history(input_series,0)
ensembles=result['ensemble']
ensembles.reverse()
print 'ensembles %s' %ensembles

#result = ensemble.forecast(input_series, 1)
#print 'result %s' %result
#prediction = result["expected_value"][0]
#low, high = result["predictions"][0]
#output = {"forecast": prediction, "low": low, "high": high}
#print 'output %s' %output
