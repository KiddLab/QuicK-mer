#!/usr/bin/env python

import fileinput

n = 0
for line in fileinput.input():
    line  = line.rstrip()
    line = line.split()
    print '>0\n%s\n' % (line[4])
    print '>0\n%s\n' % (line[4])

