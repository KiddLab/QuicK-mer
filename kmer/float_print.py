#!/usr/bin/env python

#this script print the binary data into string format
import sys
import struct

floatdata = open(sys.argv[1],'rb')

for i in range(1000):
	cordepth = struct.unpack('f',floatdata.read(4))[0]
	print str(cordepth)
