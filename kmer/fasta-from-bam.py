#!/usr/bin/env python
# Author: Jeffrey M Kidd
# fasta-from-bam.py
# 2014-11-07
# print out fasta from BAM for kmer pipeline
# do not keep track of the read pair info
# print to standard out


import sys
import os
import signal

from optparse import OptionParser


USAGE = """
 fasta-from-bam.py --in <BAM file> --nodup <do not include duplicate reads>
 
  Prints out fasta file from BAM to std out
  If --nodup is set, does not print out PCR duplicates

"""
parser = OptionParser(USAGE)
parser.add_option('--in',dest='inBAM', help = 'input BAM file')
parser.add_option('--nodup',dest='noDup',action='store_true', default = False, help = 'do not print out marked duplicates')
parser.add_option('--rg',dest='readgroup', help = 'Read Group info')

(options, args) = parser.parse_args()

if options.inBAM is None:
    parser.error('input BAM not given')
###############################################################################

# print 'Processing BAM file %s' % (options.inBAM)


if options.noDup is False:
    # remove not primary alignment, fails vendor QC, or supplementary alignment
    cmd = 'samtools view -F 2816 '
elif options.noDup is True:
    # remove not primary alignment, fails vendor QC, or supplementary alignment, and PCR/optical duplicates
    cmd = 'samtools view -F 3840 '

if options.readgroup != None:
    cmd += '-r '+options.readgroup+' '

cmd += options.inBAM

# print cmd


#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # To deal with fact that might close file before reading all

try:
    inFile = os.popen(cmd, 'r')
except:
    print "ERROR!! Could not open the file " + options.inBAM + " using samtools view -c\n"
    sys.exit(1)
 

for line in inFile:
    line = line.rstrip()
    line = line.split()
    name = line[0]
    seq = line[9]
    sys.stdout.write('>%s\n%s\n' % (name,seq))
inFile.close()

