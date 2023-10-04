#!/usr/bin/env python3

from distutils.errors import UnknownFileError
import sys, re, os, getopt, ragu_file
import datetime
from pathlib import Path
from pydub import AudioSegment
import mutagen
from mutagen import File as audioFile
from random import randrange
from math import floor

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass

class getTags:
    def __init__(self,path=None):
        self.path=path
        self.audio_file = None

    def getPath(self,path):
        if path != None:
            return(path)
        else:
            return(self.path)

    def plainText(self,path=None):
        self.path=self.getPath(path)
        self.audio_file=audioFile(self.path)
        tags=set(self.audio_file.tags)
        tags=set([str(self.audio_file.tags[tag]) for tag in self.audio_file.tags])
        return(tags)

class parsedTime:
    def __init__(self,time_str):
        self.hours=0
        self.minutes=0
        self.seconds=0
        self.milliseconds=0
        self.split_time(time_str)
        self.time_delta=datetime.timedelta(hours=self.hours,minutes=self.minutes,seconds=self.seconds,milliseconds=self.milliseconds)

    def split_time(self,time_str):
        try:
            hrs_mins_seconds=time_str.split(':')
        except:
            hrs_mins_seconds=[time_str]

        if len(hrs_mins_seconds) == 3:
            self.hours=int(hrs_mins_seconds.pop(0))

        if len(hrs_mins_seconds) == 2:
            self.minutes=int(hrs_mins_seconds.pop(0))

        try:
            seconds_milliseconds=(hrs_mins_seconds.pop(0)).split('.')
        except:
            seconds_milliseconds=[hrs_mins_seconds]

        if len(seconds_milliseconds) == 2:
            self.seconds=int(seconds_milliseconds.pop(0))
        
        self.milliseconds=int(seconds_milliseconds[0])

class cue_time:
    def __init__(self,path):
        raw_times=self.getFile(path)
        self.time_list=self.getTimes(raw_times)
    
    def getFile(self,path):
        out_list=[]
        with open(path, 'r', encoding='utf8') as f:
            times=f.readlines()
        
        for time in times:
            out_list.append(time.replace("\n",""))

        return(out_list)
    
    def getTimes(self, raw_times):
        
        time_list=[]
        for time in raw_times:
            time_obj=parsedTime(time)
            time_list.append(time_obj.time_delta)
        return(time_list)

def cueGen(times1,times2):
    if len(times1.time_list) > len(times2.time_list):
        firstlist=times2
        secondlist=times1
    else:
        firstlist=times1
        secondlist=times2
    

    total_time=datetime.timedelta()
    for n,time_val in enumerate(firstlist.time_list):
        i="  "
        print(f"{i}TRACK {n + 1:02d} AUDIO")
        print(f"{i}{i}TITLE \"Track{n + 1:02d}\"")
        if n == 0:
            print(f"{i}{i}INDEX 01 00:00:00")
            total_time=secondlist.time_list[n]
            
            
        else:
            index=getIndex(total_time)
            print(f"{i}{i}INDEX 00 {index}")
            total_time+=diff
            index=getIndex(total_time)
            print(f"{i}{i}INDEX 01 {index}")
            total_time+=secondlist.time_list[n]
            
        diff=(firstlist.time_list[n] - secondlist.time_list[n])
        
def getIndex(delta_time):
    time_val=timesFromDelta(delta_time)
    return(f"{time_val['minutes']:02d}:{time_val['seconds']:02d}:{int(str(time_val['milliseconds'])[0:2]):02d}")

def timesFromDelta(delta_time):
    milli_total=delta_time.microseconds / 1000
    sec_total=delta_time.seconds
    return({
        "milliseconds": floor(milli_total) % 1000,
        "seconds": floor(sec_total) % 60,
        "minutes": floor(delta_time.seconds / 60)
    })



    


def main(argv):
    # defaults    
    try:
        opts, args = getopt.getopt(argv,"h1:2:")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
        

    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        elif opt in ("-1"):
            path1 = Path(arg)
        elif opt in ("-2"):
            path2 = Path(arg)


    
    
    times1=cue_time(path1)
    times2=cue_time(path2)
    cueGen(times1,times2)
        
        



if __name__ == "__main__":
    main(sys.argv[1:])