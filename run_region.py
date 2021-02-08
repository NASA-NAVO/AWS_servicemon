#!/bin/env python

import sys
from datetime import datetime

from start_region   import start_region
from run_servicemon import run_servicemon
from stop_region    import stop_region

def main():

    if len(sys.argv) < 2:
        print('Usage: run_region.py <region_name>\n')
        sys.exit(0)


    else:
        region_name = sys.argv[1]

        starttime = datetime.now()

        start_region  (region_name)
        run_servicemon(region_name)
        stop_region   (region_name)

        logfile = open('logfile.txt', 'a+')

        endtime = datetime.now()

        logfile.write('Region ' + region_name + ' servicemon: ' + str(starttime) + ' to ' + str(endtime) + '\n')
        logfile.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
