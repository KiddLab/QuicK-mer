#!/usr/bin/env python

import subprocess
import threading
import sys
import time
import os
import argparse
import glob

parser = argparse.ArgumentParser(description='K-mer CNV pipeline')
parser.add_argument('-B',action='store_true',help="Input is bamfile")
parser.add_argument('-N',action='store_true',help="RNA Seq, no GC correction")
parser.add_argument('-o',help="Output file prefix or folder")
parser.add_argument('-r',help="Read Group Name")
parser.add_argument('input',help="File path to input bam file")
parser.add_argument('kmer',help="Directory containing the unique kmer list(.bed), excluded region(.bed) and bloom counter (.bc)")
args = parser.parse_args()

sample_path = args.input
data_path = args.kmer
if data_path[-1]=='/':
    prefix = data_path.split('/')[-2]
else:
    prefix = data_path.split('/')[-1]

if os.path.exists(data_path):
    globfile=glob.glob(data_path+"/"+prefix+"_uniq.bc")
    if len(globfile) == 1:
        bloom_counter = globfile[0]
    globfile=glob.glob(data_path+"/*.bed")
    if len(globfile) == 1:
        bedfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_GC.bin")
    if len(globfile) == 1:
        GCfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_CN2.bin")
    if len(globfile) == 1:
        CNfile = globfile[0]
    globfile=glob.glob(data_path+"/*"+prefix+"_kmer.bed")
    if len(globfile) == 1:
        uniqkmer = globfile[0]

if args.o != None:
    output = args.o
else:
    if args.B:
        output = sample_path.replace('.bam','')
    else:
        output = sample_path.replace(".fastq.gz","").replace("*","")

print bloom_counter
print GCfile
print CNfile
print uniqkmer

print time.strftime("%H:%M:%S")
if args.B:
    cmd = 'fasta-from-bam.py --nodup --in='+sample_path
    if args.r != None:
        cmd += ' --rg='+args.r
    cmd+=' |jellyfish-2 count -m 30 -C -s 3G -t 8 --bc '+bloom_counter+' /dev/fd/0 -o '+output+'.jf'
else:
    cmd = 'zcat '+sample_path+' | jellyfish-2 count -m 30 -C -s 3G -t 8 --bc '+bloom_counter+' /dev/fd/0 -o '+output+'.jf'
print cmd
subprocess.call(cmd,shell=True)

if not args.N:
    print time.strftime("%H:%M:%S")+': Start GC correction'
    cmd = 'KmerCor -l '+output+'.jf -k '+uniqkmer+' -G '+GCfile+' -E '+CNfile
    print cmd
    
    print '\n=========='
    logs = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).communicate()[0]
    print logs
    print '==========\n'
else:
    #RNA Seq
    cmd = 'cut -f5 '+uniqkmer+' | jellyfish-2 query -i '+output+'.jf'+' | python txt2bin.py /dev/fd/0 >'+output+'_result.bin'
    print cmd
    subprocess.call(cmd, shell=True)

subprocess.call('rm '+output+'.jf',shell=True)
print time.strftime("%H:%M:%S")
print 'KMER Pipeline finished'
