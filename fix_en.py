#!/usr/bin/env python3

import sys
from ragu_cjk import isCJK
from ragu_file import readCsv, writeDictstoCsv

def verifyCJK(artist_name,en_name):
    for chr in artist_name:
        if isCJK(chr) == True:
            return(en_name)
    
    return("")

def main(argv):
    file_name=argv[0]
    artist_list=readCsv(file_name,"\t")
    new_list=[]
    header=[]

    for artist in artist_list:
        artist_name=artist['artist']      
        en_name=artist['en_name']
        en_name=verifyCJK(artist_name,en_name)
        new_list.append({"artist": artist_name, "en_name": en_name})

    for k,v in new_list[0].items():
        header.append(k)

    writeDictstoCsv(new_list,file_name + '.new' + '.csv',',',overwrite=True)




if __name__ == "__main__":
    main(sys.argv[1:])