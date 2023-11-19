#!/usr/bin/env python3

import sys, os, re, requests, json, datetime, argparse, ragu_file, ragu_csv, discogs_client
from pathlib import Path
from ragu_lang import convCharset
from ragu_file import readFile
from math import floor


class discogs():
    def __init__(self,token_file='discogs_token.txt'):
        root_path=os.path.abspath(__file__)
        self.token=readFile(Path(os.path.dirname(root_path)).joinpath(token_file))
        self.dc=discogs_client.Client('kanji_to_roman/0.1', user_token=self.token)
        self.dc.set_timeout(connect=10,read=10)

    def genArtists(self,artist_name):
        try:
            results = self.dc.search(artist_name, type='artist')
        except:
            return(False)
        
        for result in results:
            id=result.id
            try:
                curr_artist=self.dc.artist(id)
            except:
                return(False)
            yield(curr_artist)

    def compileNameList(self,artist):
        name_list=[]
        for key in ['name','real_name','name_variations','aliases']:
            try:
                key_val=getattr(artist, key)
            except discogs_client.exceptions.HTTPError as e:
                key_val=None
            if key_val == None or type(key_val) == discogs_client.Artist:
                continue
            if type(key_val) == list:
                [name_list.append(n) for n in key_val]
            else:
                name_list.append(key_val)
        return(name_list)


    def matchArtist(self,match_name,best_guess=False):
        for artist in self.genArtists(match_name):
            if best_guess == True:
                first_match=artist

            name_list=self.compileNameList(artist)
            for name in name_list:
                if type(name) != discogs_client.Artist and name.strip().replace(' ','') == match_name.strip().replace(' ',''):
                    return(artist,name_list)
            
        if best_guess == True and len(first_match) > 0:
            return(first_match,self.compileNameList(first_match))

        return(False,False)


# def cmdParser():
#     default_input='artistnames.txt'
#     default_output_prefix='jp_artist_list_'
#     default_output=getOutputFilename(default_output_prefix)
#     default_delimiter="\t"
#     default_vgmdb_address='http://localhost'

#     parser = argparse.ArgumentParser(description='Query VGMDB with names to extract kanji, kana, and romaji versions of a name')
#     # Optional argument
#     parser.add_argument('-i','--input',type=str,default=default_input,help='Input file (newline delimited list of names). If not set, will be ' + default_input)
#     parser.add_argument('-o','--output',type=str,default=default_output,help='Output filename (csv file). If not set, will be ' + default_output_prefix + '[datestamp]' + os.path.splitext(default_output)[1])
#     parser.add_argument('-d','--delim',type=str,default=default_delimiter,help='CSV delimiter, by default will be ' + repr(default_delimiter))
#     parser.add_argument('-a','--vgmdb_address',type=str,default=default_vgmdb_address,help='Address of VGMdb API instance. If not set, will be ' + default_vgmdb_address)
#     parser.add_argument('-v','--verbose',action='store_true',help='If set, outputs progress')
#     args = parser.parse_args()
#     global verbose, vgmdb_address
#     vgmdb_address=args.vgmdb_address
#     verbose=args.verbose
#     return(args)



def checkDiscogs(name,artist_dict):
    d=discogs
    for artist in d.genArtists(name):
        print(dir(artist))



def main(argv):
    d=discogs()
    match_artist=d.matchArtist('戸川 純')
    print(match_artist)


if __name__ == "__main__":
    #args=cmdParser()
    main(sys.argv)