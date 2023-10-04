#!/usr/bin/env python3
import sys, re, os, getopt, ragu_file, multiprocessing, math
from pathlib import Path
from mutagen.easyid3 import EasyID3

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    print("-i : input path")
    print("-o : output path")


def processMp3File(mp3_file):
    try:
        mp3_id3=EasyID3(mp3_file)
    except:
        mp3_id3={}
    
    metadata={}
    metadata["path"]=mp3_file
    for tag in ["artist","albumartist","title","tracknumber","discnumber"]:
        try:
            metadata[tag]=mp3_id3[tag]
        except:
            metadata[tag]=""

    return(metadata)

    
    

def processMp3List(mp3_list,output_path):
    output_chars=len(str(output_path.resolve()))
    remaining_chars=260 - output_chars
    if remaining_chars < 23:
        eprint("Error: Output path too long")
        sys.exit(1)
    
    char_reservoir=math.floor((remaining_chars - 6) / 3)
    

    total_cpus=multiprocessing.cpu_count()
    cpus=total_cpus - 1
    if cpus <= 0:
        cpus=1

    pool_obj = multiprocessing.Pool(processes=int(cpus))
    metadata_list=pool_obj.map(processMp3File,mp3_list)

    

    print(metadata_list)



def main(argv):
    input_path=""
    output_path=""
    try:
        opts, args = getopt.getopt(argv,"hi:o:")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
    if len(opts) == 0:
        print("No options defined")
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt == "-i":
            input_path = Path(arg)
        elif opt == "-o":
            output_path = Path(arg)
    
    try:
        print("input path: " + str(input_path.resolve()))
    except:
        eprint("Error: Invalid input path")
        sys.exit(1)
    
    try:
        print("output path: " + str(output_path.resolve()))
    except:
        eprint("Error: Invalid output path")
        sys.exit(1)


    mp3_files=list(input_path.glob('**/*.mp3'))

    processMp3List(mp3_files,output_path)

    
    



if __name__ == "__main__":
    main(sys.argv[1:])