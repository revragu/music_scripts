#!/usr/bin/env python3

import sys
import datetime
from math import floor


# misc stuff

class progressbar():
    def __init__(self,end_pos):
        self.start_time=self.getNow()
        self.curr_pos=0
        self.end_pos=end_pos
        self.time_elapsed=datetime.timedelta(microseconds=0)
        self.last_check=self.start_time

    def getNow(self):
        return(datetime.timedelta(datetime.datetime.now().microsecond))

    def updateTime(self):
        curr_delta=datetime.timedelta(microseconds=self.getNow().microsecond) - datetime.timedelta(microseconds=self.last_check.microsecond)
        self.last_check=self.getNow()
        self.time_elapsed=self.time_elapsed + curr_delta
        time_per_unit=self.time_elapsed / self.curr_pos
        estimated_completion=self.start_time * time_per_unit
        time_left=estimated_completion - self.getNow()
        return(time_left)      

    def updateBar(self):
        self.curr_pos+=1
        percent=(self.curr_pos / max) * 100
        time_left=self.updateTime().total_seconds()
        block='|'
        num_of_blocks=floor(percent / 5)
        bar='[' + f'{block*num_of_blocks:<20}' + '] ' + f'{percent:.1f}' + ' %'
        time_est=f"Time Left: {str(time_left / 60)} minutes, {str(time_left % 60)} seconds"
        out_str=bar + "\n" + time_est
        return(out_str)



def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])