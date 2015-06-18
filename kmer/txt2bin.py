#!/usr/bin/env python

import fileinput
import struct
import sys

for line in fileinput.input():
    depth = int(line.rstrip())
    out = struct.pack('b',depth)
    sys.stdout.write(out)
