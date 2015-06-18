#!/usr/bin/env python


import sys
import numpy
import math
from lowess import lowess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import struct

GC_normalize = sys.argv[1]
normalize = open(GC_normalize,'r')
x = []
y = []
stdev = []
i = 0
ave = 0
count = 0
maxCov = 0
for line in normalize:
	arr = line.split()
	x.append(float(arr[0]))
	y.append(float(arr[1]))
	stdev.append(float(arr[3]))
	i+=1
	#get the average coverage
	ave += float(arr[1])*float(arr[2])
	count += int(arr[2])
	if i >=100 and i<=300:
		maxCov = max(maxCov,float(arr[1]))
normalize.close()
maxCov = math.ceil(maxCov)
ave = ave / count

x1 = numpy.array(x[100:301], numpy.float)
y1 = numpy.array(y[100:301], numpy.float)
result = lowess(x1,y1,f=.15).tolist()
result = y[0:100]+result+y[301:401]
corfactor = []

for i in range(401):
	if result[i] != 0 :
		corfactor.append(ave/result[i])
	else:
		corfactor.append(3)
		continue
	if corfactor[i]>3: corfactor[i] = 3
	if corfactor[i]<1/3 : corfactor[i] = 1/3

fig, ax1 = plt.subplots()
ax1.plot(x,y,'b-')
ax1.set_xlabel('GC %')
ax1.set_ylabel('Average Depth')
ax1.plot([0,100],[ave,ave],'b--')
if maxCov != 1:
	ax1.axis([0,100,0,maxCov])
for t1 in ax1.get_yticklabels():
	t1.set_color('b')
ax2 = ax1.twinx()
ax2.plot(x, corfactor, 'r-')
ax2.set_ylabel('Correction Factor')
ax2.axis([0,100,0.3,3])
for t2 in ax2.get_yticklabels():
	t2.set_color('r')
plt.savefig(GC_normalize.replace('txt','png'),format='png')

sys.stdout.write(struct.pack('f'*len(corfactor), *corfactor))

