#!/usr/bin/env python3

import sys, requests, json
from ragu_csv import writeDictstoCsv
from ragu_csv import readCsv as readCsvtoDicts

def replaceInDict(name,names_csv,full_csv):
    match=[n['romaji'] for n in names_csv if n['simplified'] == name]
    if match == []:
        return(full_csv)

    for i, line in enumerate(full_csv):
        if type(match) == list:
            match=match[0]
        else:
            match=match
        
        if ',' in line['artist_romaji'] and match.lower() in line['artist_romaji'].lower():
            artist_list=line['artist_romaji'].split(',')
            for n, artist in enumerate(artist_list):
                if match.lower() == artist.lower().strip():
                    artist_list[n]=name
                else:
                    artist_list[n]=artist.strip()

                
            new_str=', '.join(artist_list)

        else:
            if match.lower() == line['artist_romaji'].lower().strip():
                new_str=name

            else:
                new_str=line['artist_romaji']

        

        full_csv[i]['artist_en']=new_str

        
        #print("1:",match)
        #print("2:",str(line['artist_romaji']))
        #print("3:",re.match(rf'(^|, ){match}(,|$)',line['artist_romaji']))
        
    return(full_csv)



def revName(name):
    split_name=name.split(' ')
    rev_name=split_name[1:] + [split_name[0]]
    rev_name_str=' '.join(rev_name)
    return(rev_name_str)

def main(argv):
    artist_list=[]
    names_csv=readCsvtoDicts('uniq_jp_names.csv',delim="\t")

    full_csv=readCsvtoDicts('en_name_fix.csv',delim="\t")

    name_list=[n for n in names_csv]
    
    for names in name_list:
        name=names['simplified']
        romaji=names['romaji']
        artist_dict={}
        artist_dict['name']=name
        artist_dict['match']=False

        name=name.strip()
        req={
            'Accept': 'application/json',
        }

        
        address='http://localhost/search/artists/' + name
        resp=requests.get(address, req)
        
        content=json.loads(resp.content)

        artists=content['results']['artists']
        rev_name=revName(name)
        print(name,"|",rev_name)
        for n,artist in enumerate(artists):
            if n == 0:
                nearest_match=revName(artist['names']['en'])

            print(artist['names']['en'])
            if artist['names']['en'].lower() == name.lower() or artist['names']['en'].lower() == rev_name.lower():
                artist_dict['match']=True
                print("match simplified:" + artist['names']['en'])
                full_csv=replaceInDict(name,names_csv,full_csv)
                break
        
        if artist_dict['match'] == False:
            rev_romaji=revName(romaji)
            for n,artist in enumerate(artists):
                if artist['names']['en'].lower() == romaji.lower() or artist['names']['en'].lower() == rev_romaji.lower():
                    print("match romaji:" + artist['names']['en'])
                    full_csv=replaceInDict(romaji,names_csv,full_csv)
            artist_dict['nearest']=nearest_match
        else:
            artist_dict['nearest']=''
        artist_list.append(artist_dict)


    writeDictstoCsv(artist_list,'simplified_names_verif_new.csv',delim="\t")
    writeDictstoCsv(full_csv,'en_name_fix_new.csv',delim="\t")





if __name__ == "__main__":
    main(sys.argv[1:])