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

int main(int argc, char * argv[])
{
    bool inverse = false;
    if (argc < 2)
    {
        std::cout << 'Not enough parameter' << std::endl;
        std::cout << 'Usage: make-control-bin [-V] /dev/fd/0' << std::endl;
        return 1;
    }
    if (argv[1] == '-V' )
    {
        inverse = true;
    }
    std::string f1;
    unsigned char flag;
    if (inverse)
        while (std::cin >> f1 >> f1 >> f1 >> f1 >> f1 >> flag)
        {
            flag = 1 - flag;
            std::cout << flag; 
        }
}
