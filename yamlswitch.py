#!/usr/bin/env python3

from distutils.errors import UnknownFileError
from datetime import datetime
import yaml, getopt, sys, os, re, ragu_file

def getYaml(input_file):
    try:
        yaml_file=yaml.safe_load(ragu_file.readFile(input_file))
    except Exception as e:
        raise UnknownFileError("Unhandled error with " + input_file + ": " + e)

    return(yaml_file)

def outputYaml(output_path,in_dict):
    with open(output_path, 'w', encoding='utf8') as out_file:
        yaml.dump(in_dict,out_file,allow_unicode=True)


def sortByTime(in_dict):
    out_dict={}
    for k, v in in_dict.items():
        split_time=k.split(':')
        if len(split_time) == 2:
            time_obj=datetime.strptime(k,'%M:%S')
        elif len(split_time) == 3:
            time_obj=datetime.strptime(k,'%H:%M:%S')
        out_dict[time_obj.strftime('%H:%M:%S')]=v
    
    return(out_dict)



def switchKV(track_dict):
    out_dict={}
    for k, v in track_dict.items():
        if re.match(r'^[0-9]+:[0-9]+.*',k):
            out_dict[k]=v
        else:
            out_dict[v]=k

    out_dict=sortByTime(out_dict)
    
    return(out_dict)


def processYaml(input_file):
    print(input_file)
    yaml_data=getYaml(input_file)
    out_dict={}

    for k, v in yaml_data.items():
        if k != "tracks":
            out_dict[k]=v
        else:
            out_dict[k]=switchKV(v)

    return(out_dict)



def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        raise(getopt.GetoptError("Invalid option "+opts))
    if len(opts) == 0:
        print("No options defined")
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-i":
            input_file = arg
        else:
            print("Invalid option: " + opt)
            sys.exit(2)

    out_dict=processYaml(input_file)
    outputYaml(input_file,out_dict)

if __name__ == "__main__":
    main(sys.argv[1:])