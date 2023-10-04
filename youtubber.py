#!/usr/bin/env python3

from distutils.errors import UnknownFileError
import sys, re, os, getopt, ragu_file, yaml
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen import id3

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    print("youtubber.py - chops up a single audio file into individual 320kbps MP3 tracks, based on timings defined in a yml file\n\
-i : input audio file\n\
-h : this\n\
there must be a valid yml file of the same name in the directory with the audio file\n\n\
example:\n",end='')
    print(\
'---\nartist: Geckoyamori\n\
date: 2010\n\
genre: Game\n\
language: English\n\
  tracks:\n\
    "0:00": "Title Screen"\n\
    "1:09": "Theme"\n\
    "1:57": "Brinstar Green"\n\
    "3:50.700": "Item Room"\n\
    "4:13": "Brinstar Red"\n\
    "6:11": "Mini-Boss"\n\
    "6:49": "Ending"\n\n',end='')
    print("\
track format is 'start time': 'title'\n\
tracks will end where the next track starts, until the last in the list, which will continue until the end of the audio file.\n\
any tag is valid, but 'artist', 'album', 'album_artist', 'date', 'composer', 'genre', 'discnumber', 'comment', 'language' \
will be given the appropriate standard tags. all other tags will be added as TXXX tags.\n\
if either artist or album_artist are missing, it will try to use the other if it exists.\n\
track numbers are sequenced based on the position in the yml file, under the 'tracks' key.\n\
individual tracks will be in the same directory, named:\n\
[track number]_[Track_name].mp3\n\n\
example:\n\
02_Brinstar Green.mp3\n",end='')
    

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


class wav_file:
    def __init__(self):
        self.input_file=None
        self.wav_path=None
        self.real_path = None
        self.file_name = None
        self.file_name_noext = None
        self.dir_path = None
        self.length = None
        self.wav = None

    def getInput(self,input_file):
        self.input_file=input_file
        try:
            self.real_path = os.path.realpath(self.input_file)
            self.file_name = os.path.basename(self.real_path)
            self.file_name_noext = re.sub(r'\.[a-z1-9]{1,4}$','',self.file_name)
            self.dir_path = os.path.dirname(self.real_path)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find " + input_file + " in " + self.dir_path)
        except Exception as e:
            raise UnknownFileError("Unhandled error finding " + input_file + " in " + self.dir_path + ": " + e)

    def convertToWav(self):
            # convert to wav
            self.wav_path=self.dir_path + "/" + self.file_name_noext + ".wav"
            initial_audio=AudioSegment.from_file(self.input_file)
            initial_audio.export(self.wav_path, format="wav")
            # get wav and length of wav
            self.wav=AudioSegment.from_file(self.wav_path)
            self.length=len(self.wav)


class youtubber:
    def __init__(self):
        self.input_file=None
        self.real_path = None
        self.file_name = None
        self.file_name_noext = None
        self.dir_path = None
        self.wav = None
        self.yaml_path = None
        self.cue_file = None
        self.cue_tracks = None
        self.tags = None

    def getInput(self,input_file):
        self.input_file=input_file
        try:
            self.real_path = os.path.realpath(self.input_file)
            self.file_name = os.path.basename(self.real_path)
            self.file_name_noext = re.sub(r'\.[a-z1-9]{1,4}$','',self.file_name)
            self.dir_path = os.path.dirname(self.real_path)
            
        except FileNotFoundError:
            raise FileNotFoundError("Could not find " + input_file + " " + e)
        except Exception as e:
            raise UnknownFileError("Unhandled error finding " + input_file + " " + e)


    def getTiming(self,time_str):
        millisecond=int(0)
        if '.' in time_str:
            split_milli=time_str.split('.')
            second=getSecond(split_milli[0])
            millisecond=int(str(split_milli[1]).ljust(3,'0'))
        else:
            second=getSecond(time_str)
        

        return(second * 1000 + millisecond)

    def convertTrack(self,track_meta):
        artist=""
        n=track_meta[0]
        trackinfo=track_meta[1]
        length=str(trackinfo[0])
        if type(trackinfo[1]) == dict:
            track=trackinfo[1]['track']
        else:
            track=str(trackinfo[1])
        print("track " + track)
        curr_track=n
        #print("curr_track" + str(curr_track))
        print(str(curr_track + 1) + " / " + str(self.cue_tracks))
        track_num=str(n + 1).zfill(2)
        output_file_name=track_num + "_" + track.replace('/','_')
        start_time=self.getTiming(length)
        print("start time " + str(start_time))
        if (n + 1) < (self.cue_tracks):
            end_time=self.getTiming(str([next_track for next_track in (list(self.cue_file["tracks"].items()))[curr_track + 1]][0]))
        else:
            end_time=self.wav.length
        
        print("end time " + str(end_time))

        extract = self.wav.wav[start_time:end_time]

        mp3_filepath=self.dir_path + "/" + output_file_name +'.mp3'

        extract.export(mp3_filepath, format="mp3", bitrate="320k")

        # tagging
        
        # necessary tags
        self.tags = id3.ID3()
        # artist
        # album
        # track title
        self.tags.add(id3.TIT2(text=track))
        # track number / total tracks
        self.tags.add(id3.TRCK(text=(str(n + 1) + '/' + str(self.cue_tracks))))
        # set disc number to 1/1, change if there's an actual disc number
        self.tags.add(id3.TPOS(text="1/1"))
        # add a from youtube tag
        self.tags.add(id3.TXXX(desc="source",text="Youtube"))


        # optional tags
        for k,v in self.cue_file.items():
            if v == None:
                continue
            tag=k.lower()
            if tag != 'tracks':
                self.tagTrack(tag,k,v)

        # for compilations using dicts
        if type(trackinfo[1]) == dict:
            for k,v in trackinfo[1].items():
                if v == None:
                    continue
                tag=k.lower()
                if tag != 'track':
                    self.tagTrack(tag,k,v)

        if self.tags.getall('TPE2') and not self.tags.getall('TPE1'):
            self.tags.add(id3.TPE1(text=(self.tags.getall('TPE2'))[0].text))

        if self.tags.getall('TPE1') and not self.tags.getall('TPE2'):
            self.tags.add(id3.TPE2(text=(self.tags.getall('TPE1'))[0].text))

        # save self.tags
        self.tags.save(mp3_filepath)
        

    def tagTrack(self,tag,k,v):
        if tag == 'artist':
            self.tags.add(id3.TPE1(text=v))
        elif tag == 'album':
            self.tags.add(id3.TALB(text=v))
        elif tag == 'album_artist':
            self.tags.add(id3.TPE2(text=v))
        elif tag == 'date':
            self.tags.add(id3.TDRC(text=v))
        elif tag == 'composer':
            self.tags.add(id3.TCOM(text=v))
        elif tag == 'genre':
            self.tags.add(id3.TCON(text=v))
        elif tag == 'discnumber':
            self.tags.add(id3.TPOS(text=v))
        elif tag == 'comment':
            self.tags.add(id3.COMM(text=v))
        elif tag == 'language':
            self.tags.add(id3.TLAN(text=v))
        else:
            self.tags.add(id3.TXXX(desc=tag,text=v))
        

    def cutTrack(self):
        #cpus=math.floor((int(multiprocessing.cpu_count()) / 4))
        #if cpus <= 0:
        #    cpus=1


        #pool_obj = multiprocessing.Pool(processes=cpus)
        

        # get directory
        # open cue
        try:
            self.yaml_path=self.dir_path + "/" + self.file_name_noext + ".yml"
            self.cue_file=yaml.safe_load(ragu_file.readFile(self.yaml_path))
        except Exception as e:
            raise UnknownFileError("Unhandled error finding " + self.input_file + " in " + self.dir_path + ": " + e)

        # convert to wav
        self.wav=wav_file()
        self.wav.getInput(self.input_file)
        self.wav.convertToWav()

        # number of tracks in cue file
        self.cue_tracks=len(self.cue_file["tracks"])

        # process cue
        meta_list=[]
        for n, trackinfo in enumerate(self.cue_file["tracks"].items()):
            track_meta=[n,trackinfo]
            #meta_list.append(track_meta)
            self.convertTrack(track_meta)
        
        #pool_obj.map(self.convertTrack,meta_list)
        
        
        
        """ mp3_file = MP3(mp3_filepath)
            # artist
            # album
            # track title
            mp3_file.tags["TIT2"]=id3.TIT2(text=track)
            # track number / total tracks
            mp3_file["TRCK"]=id3.TRCK(text=(str(n + 1) + '/' + str(cue_tracks)))
            # set disc number to 1/1, change if there's an actual disc number
            mp3_file["TPOS"]=id3.TPOS(text="1/1")

            # optional tags
            for k,v in cue_file.items():
                tag=k.lower()
                if tag != 'tracks':
                    val=v.lower()
                    if tag == 'artist':
                        mp3_file["TPE1"]=id3.TPE1(text=v)
                    elif tag == 'album':
                        mp3_file["TALB"]=id3.TALB(text=v)
                    elif tag == 'album_artist':
                        mp3_file['TPE2']=id3.TPE2(text=v)
                    elif tag == 'date':
                        mp3_file['TDRC']=id3.TDRC(text=v)
                    elif tag == 'composer':
                        mp3_file['TCOM']=id3.TCOM(text=v)
                    elif tag == 'genre':
                        mp3_file['TCON']=id3.TCON(text=v)
                    elif tag == 'discnumber':
                        mp3_file['TPOS']=id3.TPOS(text=v)
                    elif tag == 'comment':
                        mp3_file['COMM']=id3.COMM(text=v)
                    elif tag == 'language':
                        mp3_file['TLAN']=id3.TLAN(text=v)
                    else:
                        mp3_file['TXXX']=id3.TXXX(desc=tag,text=v)
                        mp3_file['TXXX']=id3.TXXX(desc="test",text="testtest")

            if ('TPE1' in mp3_file.keys()) and ('TPE2' not in mp3_file.keys()):
                mp3_file['TPE2']=id3.TPE2(text=mp3_file['TPE1'].text)

            # save tags
            mp3_file.save() """

def main(argv):
    get_rom=False
    try:
        opts, args = getopt.getopt(argv,"hi:")
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
            input_file = arg
    
    print("input file: " + input_file)
    youtub=youtubber()
    youtub.getInput(input_file)
    #try:
    youtub.cutTrack()
    #except Exception as e:
    #    eprint("error in: " + input_file + " - " + str(e))
        
        



if __name__ == "__main__":
    main(sys.argv[1:])