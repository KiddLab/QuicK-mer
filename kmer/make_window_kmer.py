#!/usr/bin/env python

import sys
#This script is used to generate kmer window with argument 1 how many kmers per window and 2 the file to sorted uniq kmer list
mers_per_window = int(sys.argv[1])
kmer_list = open(sys.argv[2],'r')

cur_chro = ''
bin_count = 0
bin_start = 0
bin_end = 0

for line in kmer_list:
    arr = line.split()
    #Use lower end of center as position, thus +15
    kmer_pos = int(arr[1])+15
    if  arr[0] != cur_chro:
        if cur_chro != '':
            print cur_chro+'\t'+str(bin_start)+'\t'+str(bin_end)+'\t'+str(bin_count) 
        bin_count = 0
        bin_start = 0
        bin_end = 0
        cur_chro = arr[0]
    elif mers_per_window == bin_count:
        bin_end = int(bin_end+kmer_pos)/2
        print cur_chro+'\t'+str(bin_start)+'\t'+str(bin_end)+'\t'+str(mers_per_window)
        bin_start=bin_end+1
        bin_count= 0
    bin_count += 1
    bin_end = kmer_pos

print cur_chro+'\t'+str(bin_start)+'\t'+str(bin_end)
