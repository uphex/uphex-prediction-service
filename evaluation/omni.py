import sys
import numpy

def median(lst):
	return numpy.median(lst)
def stdev(lst):
	return numpy.std(lst)

def main():
	size_set=50
	filename=sys.argv[1]
	outfilename=filename+".perfect"
	x=numpy.loadtxt(filename,delimiter=',',skiprows=1,usecols=(1,))
	length_array=x.size
	iterations=int(length_array/size_set)+1
	outputtotal=numpy.ndarray(shape=(0,0))
	for i in range(1,(iterations+1)):
		minelement=(size_set*(i-1))-1
		if i==1: minelement=0
		maxelement=(size_set*i)-1
		totalset=x[range(1,maxelement)]
		set=x[range(minelement,maxelement)]
		print(set)
		value=max(median(totalset),median(set))+2*max(stdev(totalset),stdev(set))
		print("med for iteration "+str(i))
		print(value)
		outputset=1*(set>numpy.array(value))
		print(outputset)
		outputtotal=numpy.append(outputtotal,outputset)
	print(outputtotal)
	numpy.savetxt(outfilename,outputtotal)
		

if __name__ == '__main__':
	main()
