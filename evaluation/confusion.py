import sys

#initialize the fill confusion hash
def fill_confusion_hash(keys):
	confusionh={}
	for key in keys:
		for key2 in keys:
			str=key+'_'+key2
			confusionh[str]=0
	return(confusionh)

#read the file and fill the confusion hash
def read_and_fill_file(file,confusionh):
	header=True
	f=open(file,'rb')
	for line in f:
		if not header:
			(channel,metric,time,observation,pred_value,pred_low,pred_high,anomalous,human)=line.strip().split(',')
			if(anomalous==''): anomalous='No' 
			if(human==''): human='No'
			if(human=='N'): human='No'
			if(human=='A' or human=='Y'): human='Yes'
			key=anomalous+'_'+human
			confusionh[key]+=1
		else:
			header=False
	f.close()
	return(confusionh)

#generate metrics based off confusion matrix
def metrics_confusion_matrix(confusionh):
	#initiate variables
	accuracy_rate_num=0
	accuracy_rate_denom=0
	hit_rate_num=0
	hit_rate_denom=0
	
	#loop through keys
	for key in confusionh.iterkeys():
		value=confusionh[key]
		(predicted,actual)=key.split('_')
		#accuracy rate
		if(predicted==actual): accuracy_rate_num+=value
		accuracy_rate_denom+=value
		#hit rate
		if(predicted=='Yes'):
			if(predicted==actual): hit_rate_num+=value
			hit_rate_denom+=value
		# print predicted+' '+actual+' '+str(value)
	accuracy_rate=float(accuracy_rate_num)/accuracy_rate_denom if accuracy_rate_denom!=0 else 0
	hit_rate=float(hit_rate_num)/hit_rate_denom if hit_rate_denom!=0 else 0
	print
	print 'acuracy rate '+str(accuracy_rate)
	print 'hit rate '+str(hit_rate)
	return(accuracy_rate,hit_rate)

def main():
	if(len(sys.argv)!=2): sys.exit('run like this: python confusion.py observations.csv')
	keys=['No','Yes']
	confusionh=fill_confusion_hash(keys)
	file=sys.argv[1]
	confusionh=read_and_fill_file(file,confusionh)
	(accuracy_rate,hit_rate)=metrics_confusion_matrix(confusionh)

if __name__ == '__main__':
	main()
