//
//  kmer2window.cpp
//  
//
//  Created by Feichen on 1/26/15.
//
//

#include <cstdlib>
#include <cstdio>
#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <string>
#include <map>
#include <iterator>
#include <cmath>
#include <iomanip>

struct chrloc
{
    unsigned char chr_idx;
    unsigned int chr_begin;
    unsigned int chr_end;
    float depth;
};

int main(int argc, char * argv[])
{
    std::ifstream kmer_bin;
    std::ifstream window_file;
    kmer_bin.open(argv[1], std::ifstream::in | std::ifstream::binary);
    window_file.open(argv[2], std::ifstream::in);
    //Read in window file
    std::string chr,last_chr;
    unsigned int bin_start, bin_end, bin_count;
    unsigned int index=0;
    //First line
    window_file >> chr >> bin_start >> bin_end >> bin_count;
    std::vector<chrloc> coordinate;
    std::vector<std::string> chromosome;
    chromosome.push_back(chr);
    last_chr = chr;
    chrloc mychrloc;
    float *depth_bin = new float [bin_count];
    unsigned char *control_region = new unsigned char [bin_count];
    window_file.seekg(0,std::ifstream::beg);
    unsigned int control_count = 0;
    while (window_file >> chr >> bin_start >> bin_end >> bin_count)
    {
        //Read Bin files
        kmer_bin.read((char*)depth_bin,bin_count*4);
        float ave = 0.;
        unsigned short bool_sum=0;
        unsigned int effective_mers = 0;
        for (int i = 0; i < bin_count; i++)
        {
            if (depth_bin[i] != 0.0)
            {
                ave += depth_bin[i];
                effective_mers++;
            }
        }
        if (effective_mers != 0)
            ave /= effective_mers;
        if (chr != last_chr)
        {
            chromosome.push_back(chr);
            last_chr = chr;
        }
        if (bin_start!=0) bin_start--;
        mychrloc.chr_begin = bin_start;
        mychrloc.chr_end = bin_end;
        mychrloc.chr_idx = chromosome.size()-1;
        mychrloc.depth = ave;
        coordinate.push_back(mychrloc);
        index++;
    }
	for (int i = 0; i < coordinate.size(); i++)
	{
		std::cout << chromosome[coordinate[i].chr_idx] <<'\t'<< coordinate[i].chr_begin <<'\t'<< coordinate[i].chr_end;
		std::cout << std::fixed;
		std::cout << std::setprecision(3) <<'\t'<< coordinate[i].depth << std::endl;
	}
}
