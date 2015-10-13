import sys
import numpy

def median(lst):
	return numpy.median(lst)
def stdev(lst):
	return numpy.std(lst)

def main():
	size_set=50 #size of set to read
	filename=sys.argv[1] #filename to be read, passed as argv
	outfilename=filename+".perfect" #outputfilename...cat perfect on end
	ox=numpy.loadtxt(filename,delimiter=',',skiprows=1,usecols=(1,)) #read data
	x=ox[::-1] #reverse so that it is ascending by date
	length_array=x.size #length of array
	iterations=int(length_array/size_set)+1 #number of iterations depending on size of set
	outputtotal=numpy.ndarray(shape=(0,0)) #initalize array
	for i in range(1,(iterations+1)): #foreach range
		minelement=(size_set*(i-1))-1 #min index of iteration set
		if i==1: minelement=0 #first run through would return -1..we want it to return 0
		maxelement=(size_set*i)-1 #max index of iteration set
		totalset=x[range(1,maxelement)] #entire set including all iterations
		set=x[range(minelement,maxelement)] #iteration set
		print(set)
		value=max(median(totalset),median(set))+2*max(stdev(totalset),stdev(set)) #max(totalset_median,iterationset_median)+2*max(totalset_stdev,iterationset_stdev)
		lowervalue=min(median(totalset),median(set))-2*max(stdev(totalset),stdev(set))
		value=median(set)+2*stdev(set)
		lowervalue=median(set)-2*stdev(set)
		print("med for iteration "+str(i))
		print(value)
		outputset=1*((set>numpy.array(value))|(set<numpy.array(lowervalue))) #figure out if elements are greater than value obtained above
		print(outputset)
		outputtotal=numpy.append(outputtotal,outputset) #catenate the elements from previous iterations together
	print(outputtotal)
	finaloutput=outputtotal[::-1] #reverse so we can get back in the right format
	numpy.savetxt(outfilename,finaloutput) #output the file
		

if __name__ == '__main__':
	main()
