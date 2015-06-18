#!/usr/bin/env python

import sys
import struct

#Calulate average depth from bin file into the defined window

coverage = {}
#load window file
window = open('kmer/mm10/mm10_50_window.bed')
for line in window:
	arr = line.split()
	if arr[0] in coverage:
		coverage[arr[0]].append([int(arr[1]),int(arr[2]),0.,0])
	else:
		coverage[arr[0]] = []
		coverage[arr[0]].append([int(arr[1]),int(arr[2]),0.,0])
window.close()

cordinatefile = open('kmer/mm10/mm10_kmer.bed','r')
floatdata = open(sys.argv[1],'rb')

lastchr=''
#line by line to add into the list
for line in cordinatefile:
	arr = line.split()
	position = int(arr[1])+15
	cordepth = struct.unpack('f',floatdata.read(4))[0]
	#print cordepth
	#new chrmosome or not
	try:
		if lastchr != arr[0]:
			if arr[0] in coverage:
				lastchr = arr[0]
				cur_win = 0
			else:
				continue
		else:
			while not (position >= coverage[arr[0]][cur_win][0] and position <= coverage[arr[0]][cur_win][1]):
				#print coverage[arr[0]][cur_win][2]/coverage[arr[0]][cur_win][3]
				cur_win +=1
			coverage[arr[0]][cur_win][2] += cordepth
			coverage[arr[0]][cur_win][3] += 1
	except:
		print line


for key in coverage:
	for entry in coverage[key]:
		if not (entry[3] ==0):
			print str(key)+'\t'+str(entry[0])+'\t'+str(entry[1])+'\t'+str(entry[2]/entry[3])
		else:
			print str(key)+'\t'+str(entry[0])+'\t'+str(entry[1])+'\t0'
