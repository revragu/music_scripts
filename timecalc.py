#!/usr/bin/env python3
# calculator to take a file with a list of durations and convert them to timecodes

import sys
from math import floor
    


def main(argv):
    timefile=argv[0]
    time_list=[]

    with open(timefile,'r') as f:
        timelist=f.readlines()

    for t in timelist:
        split_time=t.split(":")
        hours=0
        if len(split_time) == 3:
            inc=split_time.pop(0)
            hours=int(inc) * 60 * 60

        inc=split_time.pop(0)
        mins=int(inc) * 60
        inc=split_time.pop(0)
        secs=int(inc)
        time_list.append(mins + secs)

    lasttime=0
    for t in time_list:
        curr_time=t + lasttime
        #print(curr_time)
        hours = floor((curr_time / 60) / 60)
        if hours < 1:
            hours=0
        mins=floor((curr_time % 3600) / 60)
        secs=curr_time % 60
        lasttime=curr_time
        print(str(f"{hours:02d}") + ":" + str(f"{mins:02d}") + ":" + str(f"{secs:02d}"))


if __name__ == "__main__":
    main(sys.argv[1:])