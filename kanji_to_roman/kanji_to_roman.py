#!/usr/bin/env python3

import os, re, json, datetime, argparse
from ragu_lang import convCharset, isCJK, isKana, isRoman
from pathlib import Path
from discogs_query import discogs
from ragu_file import readFileToList
from ragu_stuff import progressbar
from ragu_http import httpReq
from ragu_csv import writeDictstoCsv


# surname should come first, so determine which name is the surname. should match kana. 
# store in separate column just in case we're wrong, in the case of weird preferred romanization, or if both are the same, 
def decideCorrectRomaji(artist_dict):
    romaji=artist_dict['romaji'].lower()
    romaji_rev=artist_dict['romaji_rev'].lower()
    # if they're the same in both orders, just return
    if romaji == romaji_rev:
        return(artist_dict['romaji'])
    
    # try the kana column first, if there's no kana covert kanji, if no kanji column convert input
    if len(artist_dict['kana']) > 1:
        kana_value=convCharset(artist_dict['kana'][0],'hepburn')
    elif len(artist_dict['kanji']) > 1:
        kana_value=convCharset(artist_dict['kanji'][0],'hepburn')
    elif len(artist_dict['input']) > 1:
        kana_value=convCharset(artist_dict['input'][0],'hepburn')
    
    # split kana value to check at space
    kana_split=kana_value.split(' ')
    for i, chr in enumerate(kana_split[0]):
        if romaji.startswith(chr) and not romaji_rev.startswith(chr):
            return(artist_dict['romaji'])
        elif romaji_rev.startswith(chr) and not romaji.startswith(chr):
            return(artist_dict['romaji_rev'])
        kana_value=kana_value[i+1:]

    # if no match
    return('')

# update status bar and print status to screen if verbose. will print to the same part of the screen, so needs to do some housekeeping
def printStatus(in_str, artist, i, names_len):
    if verbose:
        string=p_bar.updateBar() + "\n" + in_str.replace("\n","") + ": "
        if artist['match'] == True:
            string+="Matched\n"
        elif artist['discogs'] == True:
            string+="Matched discogs\n"
        elif artist['best_guess'] == True:
            string+="Best Guess\n"
        elif artist['kakasi_convert'] == True:
            string+="Auto-Converted Input\n"
        else:
            string+="Error\n"

        json_dump=json.dumps(artist,indent=4,ensure_ascii=False)
        out_str=string+str(json_dump)
        out_list=out_str.split("\n")
        
        # each new entry should clear old ones from the screen
        # fill line to column width with spaces, carriage return, then print status line
        line_width = os.get_terminal_size().columns
        for n, l in enumerate(out_list):
            print(" "*line_width,end="\r")
            print(l)

        # move cursor to first line for next entry
        # for i in range(1,len(out_list) + 2):
        #     print("")
        #     print('\033[3A')

# assign to the correct charset
def assignCharset(name,artist_dict):
    # check if we can split it
    for delim in [['=',''],['（','）'],['(',')']]:
        artist_dict,split=splitNames(name,artist_dict,delim[0],delim[1])
        if split == True:
            return(artist_dict)
        
    if isKana(name.strip(),strict=True,ignore_spaces=True) and artist_dict['kana'] == '':
        artist_dict['kana']=name.strip()
        artist_dict['translit']=convCharset(artist_dict['kana'],'hepburn').title()
    elif isCJK(name,strict=True) and artist_dict['kanji'] == '':
        artist_dict['kanji']=name.strip()
    elif isRoman(name.strip(),strict=True) and artist_dict['romaji'] == '':
        artist_dict['romaji']=name.strip()
        artist_dict['romaji_rev']=revName(artist_dict['romaji'])
    return(artist_dict)

def splitNames(name,artist_dict,delim='=',delim_end=''):
    split=False
    if delim in name:
        for split_name in name.split(delim):
            if delim_end != '':
                split_name=split_name.replace(delim_end,'')
            artist_dict=assignCharset(split_name,artist_dict)
            split=True
    #print(artist_dict)
    return(artist_dict,split)


def checkDiscogsArtistName(match_name,name,artist_dict):
    if isCJK(name,strict=False):
        # populate kanji, kana, translit
        artist_dict=assignCharset(name,artist_dict)

    elif artist_dict['romaji'] == '':
        artist_dict['romaji']=name.strip()
        artist_dict['romaji_rev']=revName(artist_dict['romaji'])
    return(artist_dict)



# query discogs for names
def checkDiscogs(name,artist_dict):
    
    d=discogs()
    artist,artist_names=d.matchArtist(name)
    if artist_names == False:
        return(artist_dict)
    
    # add all names from discogs, because they're sorted poorly and basically impossible to discern birth names from stage names and aliases, so might as well have the lot of them to choose from
    out_names=[str(n) for n in artist_names]
    artist_dict['discogs_names']=', '.join(out_names) 

    
    # artist name is the most accurate (for our purposes, we only care about the artist's preferred representations)
    artist_dict=checkDiscogsArtistName(name,artist.name,artist_dict)

    # go through the name list to fill in the blanks
    if len(artist_names) > 0 and (artist_dict['kanji'] == '' or artist_dict['kana'] == '' or artist_dict['romaji'] == ''):
        for artist_name in artist_names:
            if type(artist_name) == str:
                artist_dict=assignCharset(artist_name,artist_dict)
            else:
                continue

    if len(artist_names) > 0:
        artist_dict['discogs_url']=artist.url
        artist_dict['discogs']=True
    else:
        artist_dict['discogs']=False
    return(artist_dict)

# reverse order of names
def revName(name):
    split_name=name.split(' ')
    rev_name=split_name[1:] + [split_name[0]]
    rev_name_str=' '.join(rev_name)
    return(rev_name_str)


# get the jp name from variations and return in preferred charset
def forceJP(content,charset):
    if 'Variations' in content['info'].keys():
        names=content['info']['Variations']
        for name in names:
            if 'ja' in name['names'].keys():
                return(convCharset(name['names']['ja'],charset))
            else:
                return('')
    else:
        return('')



def getHttp(address,append_address,req):
    content, status_code=httpReq(address,req,append_address)
    if status_code == 0:
        raise ConnectionError(f"Could not connect to VGMdb API server at {address}. Is it running?")
    return(content)

    


# get info from vgmdb results
def getInfo(artist,name_info):
    if artist == {}:
        return(name_info)    

    req={
        'Accept': 'application/json',
    }
    
    content=getHttp(vgmdb_address + str('/'),artist['link'],req)

    if content == False:
        return(name_info)
    
    # if vgmdb doesn't have a name_real entry for artist, get it from the variations and force kanji
    if 'name_real' in content.keys():
        name_info['kanji']=content['name_real']
    else:
        name_info['kanji']=forceJP(content,'kanji')

    # is the kanji actually kana?
    if isKana(name_info['kanji']):
        name_info['kana']=name_info['kanji']

    if name_info['kana'] == '':
    # same for name_trans, force kana
        if 'name_trans' in content.keys():
            name_info['kana']=content['name_trans']
        else:
            name_info['kana']=forceJP(content,'kana')

    # create a transliteration for the kana
    if name_info['kana'] != None:
        name_info['translit']=convCharset(name_info['kana'],'hepburn').title()

    # add name and reversed order name
    name_info['romaji']=content['name']
    name_info['romaji_rev']=revName(name_info['romaji'])
    name_info['vgmdb_url']='https://vgmdb.net/' + artist['link']
    return(name_info)

# check vgmdb aliases
def checkAliases(name, artist):
    if 'aliases' in artist.keys():
        aliases=artist['aliases']
    else:
        return(False)
    for alias in aliases:
        if name.replace(' ','') == alias.replace(' ',''):
            return(True)
    return(False)

# process vgmdb results and populate dict. return dict and the first match (to be used as a last ditch effort)
def checkVGMdb(name,content,artist_dict):
    nearest_match={}
    name=name.replace(' ','').strip()
    artists=content['results']['artists']
    for n,artist in enumerate(artists):
        alias_check=False
        if n == 0:
            nearest_match=artist
        alias_check=checkAliases(name, artist)

        if alias_check == True:
            artist_dict=getInfo(artist,artist_dict)
            
            artist_dict['input']=name
            artist_dict['match']=True
            break

    return(artist_dict, nearest_match)
    
# use kakasi to convert the kanji. usually results are not correct
def kakasiConvert(artist_dict):
    name=artist_dict['raw_input']
    artist_dict['kanji']=name
    artist_dict['kana']=convCharset(name,'kana')
    artist_dict['romaji']=convCharset(artist_dict['kana'],'hepburn').title()
    artist_dict['romaji_rev']=revName(artist_dict['romaji'])
    artist_dict['translit']=artist_dict['romaji']
    artist_dict['kakasi_convert']=True
    return(artist_dict)

# create a list of dicts of the artist name kanji, kana, romaji. try vgmdb api, discogs, and just run a kakasi conversion as a last ditch effort
def kanjiToRoman(names_list):
    artist_list=[]
    names_len=len(names_list)

    if verbose:
        global p_bar
        p_bar=progressbar(names_len)

    for i,name in enumerate(names_list):
        artist_dict={
            "raw_input": name.strip(),
            "input": name.replace(' ','').strip(),
            "kanji": '',
            "kana": '',
            'romaji': '',
            'romaji_rev': '',
            'romaji_correct': '',
            'translit': '',
            'match': False,
            'discogs': False,
            'best_guess': False,
            'kakasi_convert': False,
            'discogs_names': '',
            'vgmdb_url': '',
            'discogs_url': ''
            
        }
        req={
            'Accept': 'application/json',
        }
        
        # query vgmdb
        content=getHttp(vgmdb_address + '/search/artists/',re.escape(name.replace(' ','').strip()),req)
        if content != False:
            # check vgmdb
            artist_dict,nearest_match=checkVGMdb(name.replace(' ','').strip(),content,artist_dict)        

        # if no match on vgmdb, try discogs
        if artist_dict['match'] == False:
            artist_dict=checkDiscogs(name.replace(' ','').strip(),artist_dict)
            # if no match on discogs, use the first match on vgmdb
            if artist_dict['discogs'] == False and nearest_match != {}:
                artist_dict=getInfo(nearest_match,artist_dict)
                if artist_dict['kana'] == '':
                    artist_dict['kana']=convCharset(name,'kana')
                if artist_dict['romaji'] == '':
                    artist_dict['romaji']=convCharset(name,'hepburn').title()
                    artist_dict['romaji_rev']=revName(artist_dict['romaji'])
                if artist_dict['translit'] == '':
                    artist_dict['translit']=convCharset(name,'hepburn').title()
                artist_dict['best_guess']=True
            elif artist_dict['discogs'] == False:
                # kakasiconvert as last ditch effort
                artist_dict=kakasiConvert(artist_dict)
        
        # decide the correct version of the romaji (should match the kana representation)
        artist_dict['romaji_correct']=decideCorrectRomaji(artist_dict)
        printStatus(name, artist_dict,i,names_len)
        

        artist_list.append(artist_dict)
    
    return(artist_list)

def getOutputFilename(default_output_prefix):
    output_root=os.path.dirname(default_output_prefix)
    output_prefix=os.path.basename(default_output_prefix)
    timestamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    output_suffix='.csv'
    return(Path(output_root).joinpath(output_prefix + str(timestamp) + output_suffix))

def main(input,output,delimiter):
    try:
        names_list=readFileToList(input)
    except FileNotFoundError as e:
        raise FileNotFoundError(f'{str(input)} not found') 
    except Exception as e:
        raise Exception(f'Cannot open file {input}' + "\n" + f'Unhandled exception: {e}')

    artist_list=kanjiToRoman(names_list)
    
    if verbose:
        print("\n"*15)
        print("Writing to dict")
    writeDictstoCsv(artist_list,Path(output),delimiter)

def cmdParser():
    root_path=os.path.dirname(os.path.abspath(__file__))
    default_input=Path(root_path).joinpath('artistnames.txt')
    default_output_prefix=Path(root_path).joinpath('jp_artist_list_')
    default_output=getOutputFilename(default_output_prefix)
    default_delimiter="\t"
    default_vgmdb_address='http://localhost'

    parser = argparse.ArgumentParser(description='Query VGMDB with names to extract kanji, kana, and romaji versions of a name')
    # Optional argument
    parser.add_argument('-i','--input',type=str,default=default_input,help='Input file (newline delimited list of names). If not set, will be ' + str(default_input))
    parser.add_argument('-o','--output',type=str,default=default_output,help='Output filename (csv file). If not set, will be ' + str(default_output_prefix) + '[datestamp]' + os.path.splitext(default_output)[1])
    parser.add_argument('-d','--delim',type=str,default=default_delimiter,help='CSV delimiter, by default will be ' + repr(default_delimiter))
    parser.add_argument('-a','--vgmdb_address',type=str,default=default_vgmdb_address,help='Address of VGMdb API instance. If not set, will be ' + default_vgmdb_address)
    parser.add_argument('-v','--verbose',action='store_true',help='If set, outputs progress')
    args = parser.parse_args()
    global verbose, vgmdb_address
    vgmdb_address=args.vgmdb_address
    verbose=args.verbose
    return(args)

if __name__ == "__main__":
    args=cmdParser()
    main(args.input, args.output, args.delim)