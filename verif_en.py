#!/usr/bin/env python3

import sys, os, csv
from ragu_cjk import isCJK
from ragu_csv import readCsv, writeDictstoCsv

def verifyCJK(artist_name):
    for chr in artist_name:
        if isCJK(chr) != "":
            return(artist_name)

    return("")


def sortNames(artists):
    jp_names=[]
    roma_names=[]
    for name in artists:
        name=name.strip()
        if verifyCJK(name) != "":
            jp_names.append(name)
            continue
        roma_names.append(name)

    return(jp_names,roma_names)

def main(argv):
    file_name=argv[0]
    artist_list=readCsv(file_name,',')
    new_list=[]
    header=[]

    for artist in artist_list:
        check=""
        artists=artist['artist'].split(',')
        en_names=artist['en_name'].split(',')

        jp_names, roma_names=sortNames(artists)
        
        if len(jp_names) != len(en_names):
            check="X"


        names=roma_names + jp_names
        artist_string=", ".join(names)

        new_list.append({"artist": artist_string, "en_name": artist['en_name'], "check": check})

    for k,v in new_list[0].items():
        header.append(k)

    writeDictstoCsv(new_list,file_name + '.new' + '.csv',',', overwrite=True)




if __name__ == "__main__":
    main(sys.argv[1:])