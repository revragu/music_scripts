#!/usr/bin/env python3

import sys, re, getopt
import datetime
from pathlib import Path
from math import floor

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass

# gets file, returns as list of strs
def getFile(path):
    out_list=[]
    with open(path, 'r', encoding='utf8') as f:
        times=f.readlines()
        
    for time in times:
        out_list.append(time.replace("\n",""))

    return(out_list)
    
def getDelta(t):
    s=t.split(':')
    mins=int(s[0])
    secs=int(s[1])
    milli=int(s[2]) * 13
    return(datetime.timedelta(minutes=mins,seconds=secs,milliseconds=milli))

def convertToCueTime(d_time):
    seconds=floor(d_time.seconds) % 60
    mins=floor(d_time.seconds / 60)
    frames=floor((d_time.microseconds / 1000) / 13) % 75
    time_out=f"{mins:02d}:{seconds:02d}:{frames:02d}"
    return(time_out)

def writeCue(path,cue_dat):
    with open(path, 'w', encoding='utf8') as f:
        f.write(cue_dat)

def runOperation(t,op,v):
    
    t_delta=getDelta(t)
    v_delta=getDelta(v)
    if op == "sub":
        v_delta=v_delta * -1
    if t_delta.seconds == 0:
        v_delta = datetime.timedelta(seconds=0)
    return(convertToCueTime(t_delta + v_delta))

def updateCue(cue,op,v,rng=""):
    if rng == "":
        rng=range(-1,len(cue) + 1)
    out_cue=""
    track=0
    for line in cue:
        if re.match(r'.*TRACK [0-9]+',line):
            track=int(re.sub(r'.*TRACK ([0-9]+).*',r'\1',line))
        if re.match(r'.*INDEX [0-9]+',line) and track in rng:
            pre=re.sub(r'(^.* [0-9]+ )[0-9]+:[0-9]+:[0-9]+$',r'\1',line)
            t=re.sub(r'^.* ([0-9]+:[0-9]+:[0-9]+)$',r'\1',line)
            out_cue+=pre + str(runOperation(t,op,v)) + "\n"
            track=-1
        else:
            out_cue+=line + "\n"
    return(out_cue)


def main(argv):
    # defaults    
    list_times=[]
    rng=""
    try:
        opts, args = getopt.getopt(argv,"hi:v:r:pm")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
        

    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        elif opt in ("-i"):
            path=Path(arg)
            cue = getFile(path)
        elif opt in ("-p"):
            op = "add"
        elif opt in ("-m"):
            op = "sub"
        elif opt in ("-v"):
            val=arg
        elif opt in ("-r"):
            s=arg.split(',')
            rng=range(int(s[0]) - 1,int(s[1]) + 1)

    

    out_cue=updateCue(cue,op,val,rng)
    print(out_cue)
    writeCue(path,out_cue)
    
        



if __name__ == "__main__":
    main(sys.argv[1:])