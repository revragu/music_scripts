#!/usr/bin/env python3

from distutils.errors import UnknownFileError
import sys, re, os, getopt, ragu_file,math,multiprocessing
from pathlib import Path
from pydub import AudioSegment
import mutagen
from mutagen import File as audioFile
from random import randrange
from operator import itemgetter

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass

def getSecond(time):
    # is this in H:M:S or S format?
    # H:M:S format, return seconds
    hours=0
    minutes=0
    seconds=0
    if ':' in time:
        split_time=time.split(':')
        if len(split_time) == 3:
            hours=int(split_time[0])
            minutes=int(split_time[1])
            seconds=int(split_time[2])
        if len(split_time) == 2:
            minutes=int(split_time[0])
            seconds=int(split_time[1])
        hours_to_secs=hours * 60 * 60
        minutes_to_secs=minutes * 60
        seconds=seconds + minutes_to_secs + hours_to_secs

        return(seconds)
            
    # return seconds otherwise
    return(int(time))

def getGenre(audio_file):
    genre=""
    tag_type=type(audio_file.tags)
    try:
        
        if tag_type == mutagen.id3.ID3:
            genre=audio_file.tags['TCON']
        elif tag_type == mutagen.flac.VCFLACDict:
            genre=audio_file.tags['Genre']
        elif tag_type == mutagen.oggopus.OggOpusVComment or tag_type == mutagen.oggvorbis.OggVCommentDict:
            genre=audio_file.tags['GENRE'][0]
        elif tag_type == mutagen.asf.ASFTags:
            genre=audio_file.tags['WM/Genre'][0]
        elif tag_type == mutagen.apev2.APEv2:
            genre=audio_file.tags['Genre']
        elif tag_type == mutagen.mp4.MP4Tags:
            genre=audio_file.tags['©gen']
    except:
        pass

    if type(genre) == list:
        out_genre=str(genre[0])
    else:
        out_genre=str(genre)
    
    if "\x00" in out_genre:
        out_genre=(out_genre.split("\x00"))[0]
    
    return(out_genre.lower())

    

def getSongData(path):
    file_size=os.path.getsize(path) / 1000 / 1000
    audio_file=audioFile(path)
    genre=getGenre(audio_file)
    song_length=audio_file.info.length
    return({"path": path, "size": file_size, "length": song_length, "genre": genre})
    
    

def getFmtWildcard(format):
    regex_out="*"
    for char in format:
        if re.match(r'[a-zA-Z]',char):
            regex_out+='['+char.upper()+char.lower()+']'
        else:
            regex_out+=char
    return(regex_out)


def fileCollector(path):
    
    formats=set([".mp3",".mp4",".m4a",".mpc",".ape",".flac",".wav",".opus",".ogg",".wma",".wv"])
    lists_by_ext=[]
    file_list=[]
    for format in formats:
        file_gen=(p.resolve() for p in Path(path).glob("**/*") if p.suffix in formats)

    for f in file_gen:
        file_list.append(f)
        #wildcard_format=getFmtWildcard(format)
        #print(wildcard_format)
        #lists_by_ext+=list(Path(path).rglob(wildcard_format))

    return(file_list)

def getMean(amt):
    total=0
    for a in amt:
        total+=a['amount']
    return(math.ceil(total / len(amt)))


def getHandicaps(genres,genre_set):
    handicaps={}
    genre_amount=[]
    for curr_gen in genre_set:
        genre_list=[g for g in genres if g == curr_gen]
        genre_amount.append({ 
            "genre" : str(curr_gen),
            "amount": len(genre_list)})
    
    #mean=getMean(genre_amount)

    sorted_amount=sorted(genre_amount, key=itemgetter('amount'))    

    median=sorted_amount[math.floor(len(sorted_amount) / 2) - 1]["amount"]

    for amt in sorted_amount:
        if amt["amount"] > median:
            handicaps[amt["genre"]]=math.floor((median / amt["amount"]) * 10000)
        else:
            handicaps[amt["genre"]]=10000

    return(handicaps)



def qualifySong(song, handicaps, length_min):
    handicap=handicaps[song["genre"]]
    rand_val=randrange(0,10000)
    if handicap > rand_val and song["length"] > length_min:
        return(song)
    else:
        return(False)

def rewriteGenres(songs, genre_groups):
    out_data=[]
    for song in songs:
        rewrite=False
        for genres in genre_groups:
            if song["genre"].lower() in genres:
                song["genre"]=genres[0]
                out_data.append(song)
                rewrite=True
                break
        if rewrite == False:
            out_data.append(song)            

    return(out_data)




def getPlaylist(path, size_max, length_min, genre_block, genre_groups):
    cpus=math.floor((int(multiprocessing.cpu_count()) - 1))
    if cpus <= 0:
        cpus=1

    pool_obj = multiprocessing.Pool(processes=cpus)

    print("getting files")
    file_lib=fileCollector(path)
    audio_info=[]
    print("getting data from files")
    audio_data=rewriteGenres(pool_obj.map(getSongData,file_lib), genre_groups)


    
    #print(audio_files)

    genres=[data['genre'] for data in audio_data]
    genre_set=set(genres)

    #print("generating genre handicaps")
    handicaps=getHandicaps(genres,genre_set)
    curr_size=0
    lib_len=len(audio_data)
    playlist=genPlaylist(audio_data, curr_size, size_max, length_min, lib_len, handicaps, genre_block)
    return(playlist)

def genPlaylist(audio_data, curr_size, size_max, length_min, lib_len, handicaps, genre_block,iteration=0):
    out_playlist=[]
    rejects=[]
    another_chance=[]

    while curr_size < size_max and lib_len > 1:
        lib_len=len(audio_data)
        rand_idx=randrange(0,lib_len - 1)
        curr_song=audio_data.pop(rand_idx)
        
        append_song=qualifySong(curr_song, handicaps, length_min)
        if append_song != False and curr_song["genre"] not in genre_block:
            curr_size+=curr_song["size"]
            out_playlist.append(curr_song["path"])
        elif curr_song["genre"] in genre_block:
            pass
        else:
            rejects.append(curr_song)
    iteration+=1

    if curr_size < size_max and len(rejects) > 0 and iteration < 100:
        lib_len=len(rejects)
        another_chance=genPlaylist(rejects, curr_size, size_max, length_min, lib_len, handicaps, genre_block, iteration)

    out_playlist.extend(another_chance)

    return(out_playlist)


def writePlaylist(playlist, m3u_path):
    with open(m3u_path, 'w', encoding='utf8') as m3u_out:
        for song in playlist:
            m3u_out.write(str(song) + "\n")

def main(argv):
    # defaults
    path=Path('d:\\music\\New Library')
    # in mb
    size_max=100000
    # in seconds
    length_min=5
    # output m3u path
    m3u_path=("playlist_random.m3u8")
    # blocked genres
    genre_block=["spoken word","karaoke","comedy","garbage","awful","sound effects"]
    
    genre_groups=[
        ["electronic","dance","disco","eurobeat","techno","chiptune"],
        ["folk","folk rock","country"],
        ["funk","r&b","soul","blues"],
        ["heavy metal","hair metal","hard rock","metal","black metal","death metal","symphonic rock"],
        ["hip-hop","reggae"],
        ["jazz","fusion","progressive rock","noise","experimental","industrial"],
        ["j-pop","enka"],
        ["modern classical","new age","classical"],
        ["punk","new wave","post-punk","synth-pop","electronic rock","noise rock","psychedelic rock","industrial metal","industrial rock","alternative rock"],
        ["pop","rock","rock & roll","indie rock","alternative rock"],
        ["soundtrack","musical"],
        ["sound effects","spoken word","parody","comedy","karaoke"],
        ["swing","tango","lounge"]
    ]



    try:
        opts, args = getopt.getopt(argv,"hp:s:l:m:g:",["help","path=","size_max=","length_min=","m3u_out=","genre_block="])
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
        

    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        elif opt in ("-p","--path"):
            path = Path(arg)
        elif opt in ("-m","--m3u_out"):
            m3u_path = Path(arg)
        elif opt in ("-s","--size_max"):
            size_max = int(arg)
        elif opt in ("-l","--length_min"):
            length_min = int(arg)
        elif opt in ("g","--genre_block"):
            genre_block = arg.split(',')
            genre_block = [g.lower() for g in genre_block]
    
    print("path: " + str(path))
    playlist=getPlaylist(path, size_max, length_min, genre_block, genre_groups)
    writePlaylist(playlist, m3u_path)

        
        



if __name__ == "__main__":
    main(sys.argv[1:])