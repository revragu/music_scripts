#!/usr/bin/env python3

import sys
import time
import datetime
from math import floor


# misc stuff

class progressbar():
    def __init__(self,end_pos):
        self.start_time=time.time()
        self.curr_pos=0
        self.end_pos=end_pos
        self.time_elapsed=0.0
        self.last_check=self.start_time

    def getNow(self):
        return(time.time())

    def updateTime(self):
        curr_delta=self.getNow() - self.last_check
        self.last_check=self.getNow()
        self.time_elapsed=self.time_elapsed + curr_delta
        time_per_unit=self.time_elapsed / self.curr_pos
        estimated_completion=self.start_time + (time_per_unit * self.end_pos)
        time_left=estimated_completion - self.getNow()
        return(int(time_left))

    def updateBar(self):
        self.curr_pos+=1
        percent=(self.curr_pos / self.end_pos) * 100
        time_left=self.updateTime()
        block='|'
        num_of_blocks=floor(percent / 5)
        bar='[' + f'{block*num_of_blocks:<20}' + '] ' + f'{percent:.1f}' + ' %'
        time_est=f"Time Left: {str(int(time_left / 60))} minutes, {str(time_left % 60)} seconds"
        out_str=bar + "\n" + time_est
        return(out_str)



def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])