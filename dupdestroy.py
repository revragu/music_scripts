#!/usr/bin/env python3

from distutils.errors import UnknownFileError
from datetime import datetime
from operator import itemgetter
from pathlib import Path
import yaml, getopt, sys, os, re, ragu_file

def usage():
    print("-i input file, tab separated list of hash + path. if no other options, will just print masters and duplicates to stdout")
    print("-m directory to move items to if moving")
    print("-d delete files")
    print("-D dry run (if deleting files)")

def getHashfile(input_file):
    out_dict={}
    with open(input_file, 'r', encoding='utf8') as f:
        lines=f.readlines()

    for line in lines:
        split_line=re.sub(r'^([a-z0-9]+)\s+(.*)',r"\1\t\2",line)
        split_line=(split_line.replace("\n","")).split("\t")
        out_dict[split_line[1]]=split_line[0]
    return(out_dict)

def sortDupes(dupes):
    if len(dupes) > 1:
        sorted_list=[]
        temp_list=[]
        for dupe in dupes:
            temp_list.append({ "dupe": Path(dupe), "len": len(dupe)})
        sorted_list=sorted(temp_list, key=itemgetter("len"), reverse=True)
        return(sorted_list)
    else:
        return([])

def getDups(dupes):
    dupe_len=len(dupes)
    master=dupes[dupe_len - 1]["dupe"]
    del dupes[dupe_len - 1]
    dupe_list=[]
    for dupe in dupes:
        dupe_list.append(dupe)
    return(master,dupe_list)

def printDups(in_dupelist):
    master,dupes=getDups(in_dupelist)
    dupe_str=str(master)
    print("Master: " + "\t" + dupe_str)
    for dupe in dupes:
        dupe_str=str(dupe["dupe"])
        print("Dupe: " + "\t" + dupe_str)

def delDups(in_dupelist,dry_run):
    master,dupes=getDups(in_dupelist)
    for dupe in dupes:
        if dry_run == False:
            os.remove(dupe["dupe"])
        else:
            print(dupe["dupe"])


def moveDups(in_dupelist,move_to):
    master,dupes=getDups(in_dupelist)
    for dupe in dupes:
        file_name=str(os.path.basename(dupe["dupe"]))
    
        dupe_path_str=str(dupe["dupe"].parent)
        dupe_path_base=re.sub(r'^(\.|\~)(\.|)','',dupe_path_str)
        new_path_str=(str(move_to) + dupe_path_base).replace('//','/')
        new_path=Path(new_path_str)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        dest_path=Path((new_path_str + '/' + file_name).replace('//','/'))
        os.rename(dupe["dupe"],dest_path)


        


def processDups(dupes, move_to, delete, dry_run):
    if len(dupes) < 1:
        return(0)
    if move_to != None:
        moveDups(dupes,move_to)
    elif delete == True:
        delDups(dupes, dry_run)
    else:
        printDups(dupes)

def dupDestroy(input_file, move_to, delete, dry_run):
    hash_dict=getHashfile(input_file)
    hashes=set([hash for key,hash in hash_dict.items()])
    for hash in hashes:
        dupes=[path for path, compare_hash in hash_dict.items() if hash == compare_hash]
        sorted_dupes=sortDupes(dupes)
        processDups(sorted_dupes, move_to, delete, dry_run)




def main(argv):
    move_to = None
    delete = False
    dry_run = False
    try:
        opts, args = getopt.getopt(argv,"hdDi:m:")
    except getopt.GetoptError:
        raise(getopt.GetoptError("Invalid option "+opts))
    if len(opts) == 0:
        print("No options defined")
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-i":
            input_file = arg
        elif opt == "-m":
            move_to = Path(arg)
        elif opt == "-d":
            delete = True
        elif opt == "-D":
            dry_run = True
        else:
            print("Invalid option: " + opt)
            sys.exit(2)
    
    dupDestroy(input_file, move_to, delete, dry_run)

if __name__ == "__main__":
    main(sys.argv[1:])