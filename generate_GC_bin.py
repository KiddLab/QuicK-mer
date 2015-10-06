#!/usr/bin/env python

import os
import commands
import fileinput
import struct
import sys
import argparse

last_chrom = ''
fasta_buf = ''
fasta_start = 0
fasta_end = 0
linesize = 51
i = 0

parser = argparse.ArgumentParser(description='QuicK-mer GC axillary file generator.')
parser.add_argument('-w',help="GC window size. Default = 400")
parser.add_argument('kmer',help="File path to kmer list")
parser.add_argument('genome',help="Directory containing FASTA file for reference genome assembly used to generate kmer list.")
parser.add_argument('output',help="File path to GC binary output.")
args = parser.parse_args()

kmerfile = open(args.kmer, 'r')
genome_path = args.genome
if genome_path[-1] != '/':
	genome_path += '/'

kmersize = len(kmerfile.readline().rstrip().split()[4])
kmerfile.seek(0)

window_size = 400
if args.w != None:
    window_size = int(args.w)

output = open(args.output,'wb')

for line in kmerfile:
	i+=1
	arr = line.split()
	chro = arr[0]
	pos = int(arr[1])
	Upstream = pos - int((window_size - kmersize)/2.0) + 1
	Downstream = pos + int((window_size + kmersize)/2.0)
	#if the file is new, open and add to dictionary
	if chro != last_chrom:
		#open corresponding chromosome files
		#print 'Opening '+chro
		chromosome= open(genome_path+chro+'.fa','r')
		fasta_buf = chromosome.read()
		#the header size
		fasta_start = fasta_buf.find('\n')+1
		#the file size
		chromosome.seek(0,2)
		fasta_end = chromosome.tell()
		chromosome.close()
		last_chrom = chro
		print chro+' loaded successfully'
	#figure out the string byte location need to chop out
	bytestart = (Upstream /(linesize -1)) * linesize + fasta_start -1 + (Upstream % (linesize-1))
	byteend = (Downstream  /(linesize -1)) * linesize + fasta_start -1 + (Downstream % (linesize-1))
	seq = fasta_buf[max(bytestart,fasta_start):min(byteend+1,fasta_end)].upper()
	#Calculate GC content
	C=seq.count('C');
	G=seq.count('G');
	A=seq.count('A');
	T=seq.count('T');
	length = A+T+C+G
	output.write(struct.pack('f',float(C+G)/length*100))
output.close()

