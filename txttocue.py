#!/usr/bin/env python3
# dirty ass script to create cue files for youtube downloads

import sys, re, os, getopt
from pathlib import Path
from ragu_cjk import isCJK

def usage():
    print("creates cue files for music downloaded from youtube based on timecodes from the description/comments (or wherever else you can get" + \
    "them from)"
    "usage: txttocue.py -i [input textfile]\n\n" + \
    "text file should be a list of timecodes and titles. i tried to make it as robust as possible to deal with whatever format you get it in," + \
    "however there are probably some funky formats that will break it.\n" + \
    "timecodes in text file must be the time the track starts, not the track length.\n" + \
    "it's expected that the file will be in a directory starting with the same name as the audio file. if not, the script will use the first" + \
    "m4a or opus file it comes across." + \
    "names and titles probably won't be perfect but hopefully enough that manually fixing them isn't too onerous"
    )

# regex subs kept ignoring the first char even if .* should be character OR anything so this is a simple parser to grab a set of chars defined by a regex
# if it finds a character in the regex, goes into run mode and appends to a string, until a character doesn't match
# returns when mode changes out of run and string meets criteria (min str len, max str len (0 = inf), a character that needs to be present)
# has special mode to detect CJK characters if regex var is set to "isCJK"  
def getString(line,regex,min_str=1,max_str=0,test_chr=None):
    is_cjk=False
    if regex=="isCJK":
        is_cjk=True
    line=str(line)
    out_string=""
    run=0
    mode="char"
    for char in line:
        match=re.match(regex,char)
        if is_cjk:
            cjk=isCJK(char,sanitize_mode=True)
            match=cjk == char
        if match:
            if mode=="char":
                mode="run"
                out_string+=char
                
            elif mode=="run":
                out_string+=char                                
        else:
            if mode == "run" and len(out_string) >= min_str and (len(out_string) <= max_str or max_str == 0) \
            and (test_chr == None or test_chr in out_string):
                return(out_string)
            else:
                out_string=""
                run=0
    
    if mode == "run" and len(out_string) >= min_str and (len(out_string) <= max_str or max_str == 0) \
    and (test_chr == None or test_chr in out_string):
        return(out_string.strip())
    else:
        return("")


# removes a year from a string. uses getYears to grab all years then subs them all out
def removeDate(datestr):
    out_str=datestr
    years=getYears(datestr)
    if len(years) >= 1:
        for year in years:
            out_str=out_str.replace(year,'')
    return(out_str.strip())

# gets all years from a string. uses getString to find all 4 chr numeric strings, puts in list, removes from string, repeats until no 4 chr numeric strings left
def getYears(yearstr):
    years=[]
    while True:
        year=getString(yearstr,r'[0-9]',4,4)
        if year != "":
            years.append(year)
            yearstr=yearstr.replace(year,'')
        else:
            break
    return(years)

# compares all int items in list for values under 10000, returns lowest value or empty str
def compareYears(year_list):
    champ=10000
    for year in year_list:
        try:
            if int(year) < champ:
                champ=int(year)
        except:
            pass
    if champ == 10000:
        return("")
    else:
        return(champ)

# removes any parentheses
def removeParentheses(string):
    string=(string.replace('(','')).replace(')','')
    string=(string.replace('{','')).replace('}','')
    string=(string.replace('[','')).replace(']','')
    string=(string.replace('<','')).replace('>','')
    return(string)

# gets file, returns as list of strs
def getFile(path):
    out_list=[]
    with open(path, 'r', encoding='utf8') as f:
        times=f.readlines()
        
    for time in times:
        out_list.append(time.replace("\n",""))

    return(out_list)

# header class, contains global cue info
class header:
    def __init__(self):
        self.title=""
        self.performer=""
        self.year=""
        self.audio_file=""
        self.en_name=""
        self.source=""

    # get the audio file based on the playlist path, will try to match the dir name to audio file but if not will use first audio file it finds
    def getAudio(self,path):
        exts=[".opus",".m4a"]
        base_name=os.path.basename(path.parent)
        file_gen=(p.resolve() for p in Path(path.parent).glob('./*') if base_name in os.path.basename(p) and p.suffix in exts)
        for f in file_gen:
            self.audio_file=os.path.basename(f)
            return(True)
        # try again if no match found - useful if characters are being substituted in case of invalid characters in dirs
        if self.audio_file == "":
            file_gen=(p.resolve() for p in Path(path.parent).glob('./*') if p.suffix in exts)
        for f in file_gen:
            self.audio_file=os.path.basename(f)
            return(True)
        else:
            return(False)

    # returns str of formatted cue data
    def printHeader(self):
        out_str=""
        if self.year != "":
            out_str+="REM DATE " + str(self.year) + "\n"
        if self.en_name != "":
            out_str+="REM EN_NAME " + str(self.en_name) + "\n"
        if self.source != "":
            out_str+="REM SOURCE " + str(self.source) + "\n"
        out_str+="PERFORMER " + '"' + str(self.performer) + '"' + "\n" + \
            "TITLE " + '"' + str(self.title) + '"' + "\n" + \
            "FILE " + '"' + str(self.audio_file) + '" WAVE' + "\n"
        return(out_str)        


# track class, contains per-track info
class track:
    def __init__(self):
        self.tracktype=""
        self.tracknum=""
        self.index=""
        self.title=""
        self.performer=""
        self.en_name=""
        self.source=""

    # returns str of formatted cue data
    def printTrack(self):
        out_str=""
        out_str="  TRACK " + f"{self.tracknum:02d}" + " " + self.tracktype + "\n" \
        "    TITLE " + '"' + self.title + '"' + "\n" \
        "    PERFORMER " + '"' + self.performer +'"' + "\n"
        if self.en_name != "":
            out_str+="    REM EN_NAME " + str(self.en_name) + "\n"
        if self.source != "":
            out_str+="    REM SOURCE " + str(self.source) + "\n"
        out_str+=        "    INDEX 01 " + str(self.index) + "\n"
        return(out_str)

# cuefile container class
class cuefile:
    def __init__(self):
        self.header=header()
        self.tracks=[]

    # gets cue data and writes cue file
    def writeCue(self,path):
        cue_file=self.printCue()
        out_path=str(path.parent) + '/' + str(os.path.basename(path.parent)) + ".cue"
        with open(out_path, 'w', encoding='utf8') as f:
            f.write(cue_file)

    # returns all cue data
    def printCue(self):
        out_str=""
        out_str+=self.header.printHeader()
        out_str+=self.printTracks()
        return(out_str)

    # returns all track data
    def printTracks(self):
        out_str=""
        for track in self.tracks:
            out_str+=track.printTrack()
        return(out_str)

    # takes path of playlist file and parses it into header data
    def getHeader(self,path):
        title=""
        performer=""
        year=""
        en_name=""
        # get dir name that playlist is in - this will be the basis of the artist/title tags
        dir_name=str(os.path.basename(path.parent))
        # make sure any weird unicode spaces are normal spaces
        dir_name=re.sub(r'‎+',' ',dir_name)
        # any other whitespace, single space
        dir_name=re.sub(r'\s+',' ',dir_name)
        # make sure any em dashes or double dashes are single dashes
        dir_name=re.sub(r'[-–—]+','-',dir_name)
        # try to split at dash
        split_name=dir_name.split('-')
        # get years
        years=[]
        year_list=getYears(dir_name)
        if len(year_list) == 1:
            years.append(year_list[0])
        elif len(year_list) > 1:
            years.append(compareYears(year_list))
        else:
            years.append("")

        # if we're able to split, we can get the data from each half. otherwise get what we can.
        title, performer, en_name=self.processSplitTitle(split_name)
        # populate header
        self.header.title=title
        self.header.performer=performer
        # get the smallest value for year (oldest date)
        self.header.year=compareYears(years)
        self.header.en_name=en_name
        self.header.source="Youtube"
        self.header.getAudio(path)


    # process the (hopefully) split directory name
    def processSplitTitle(self,split_name):
        title=""
        performer=""
        en_name=""

        # usually performer is on the left side of the title
        performer,en_name=self.getAlbumPerformer(split_name[0])

        # if we do have a split name, we can grab the title from the right. otherwise just use what we have
        if len(split_name) > 1:
            title=self.getAlbumTitle(split_name[1])
        else:
            title=self.getAlbumTitle(split_name[0])
        return(title, performer, en_name)


    # get the album performer
    def getAlbumPerformer(self, split):
        jp_chars=[]
        split_name=[]
        jp_name=""
        en_name=""
        performer=""
        # remove parentheticals
        split=removeParentheses(split)
        # remove year
        split=removeDate(split)
        # use the cjk mode of getstring to get first run of cjk characters - will be name if exists
        jp_name=getString(split,"isCJK")
        # use the sanitized string as performer if no cjk chars
        if jp_name == "":
            performer=split.strip()
        else:
            # otherwise, use cjk name as performer, then split and reverse to get en_name (haven't been able to get this to work as a special tag in cue)
            performer=jp_name
            split=split.strip()
            split_name=split.split(" ")
            if len(split_name) == 2:
                en_name=split_name[1] + " " + split_name[0]
            en_name=en_name.strip()
        
        return(performer,en_name)                
    
    # get the album title
    def getAlbumTitle(self,split):
        title=""
        # remove parentheticals
        title=removeParentheses(split)
        # remove year
        title=removeDate(title)
        # replace a bunch of common strings we don't need
        replace_strings=[r' [Ff][uU][Ll][Ll] [Aa][Ll][Bb][Uu][Mm]',r' (フル|[fF][Uu][Ll][Ll] )アルバム',r' [Rr](eissue|eupload)']
        for regex in replace_strings:
            title=re.sub(regex,'',title)
        return(title)

    # for every line of the input text file, parse for index number and title then inst a track obj and add to list, fill tags
    def getTracks(self,text_file):
        for n, line in enumerate(text_file):
            index=self.getIndex(line)
            title=self.getTitle(line)
            curr_track=track()
            curr_track.tracktype="AUDIO"
            curr_track.tracknum=n + 1
            curr_track.index=index
            curr_track.title=title
            curr_track.performer=self.header.performer
            curr_track.en_name=self.header.en_name
            curr_track.source=self.header.source
            self.tracks.append(curr_track)
        

    # sanitize line for title string
    def getTitle(self,line):
        # we need to try to remove the track numbers more than once, so i turned it into a sub func
        def removeTracknums(l):
            # remove number + period, closing parenth, colon
            l=re.sub(r'^[0-9]+[\.\)\:]','',l)
            # strip
            l=l.strip()
            # remove A-B-etc sides
            l=re.sub(r'^[A-Z][0-9]\s+','',l)
            # strip
            l=l.strip()
            # remove number + space
            l=re.sub(r'^[0-9]+\s+','',l)
            # strip
            l=l.strip()
            return(l)
        
        # remove date
        title=removeDate(line)
        # remove time
        title=title.replace(getString(title,r'[0-9\:]',4,8,':'),'')
        # remove track numbers
        title=removeTracknums(title)
        # remove beginning parentheses
        title=re.sub(r'^[\[\]\(\)\{\}\<\>]+\s+','',title)
        # remove ending parentheses
        title=re.sub(r'[\[\]\(\)\{\}\<\>][\[\]\(\)\{\}\<\>]+','',title)
        title=title.strip()
        # remove track numbers again
        title=removeTracknums(title)
        # remove beginning dashes
        title=re.sub(r'^[\-\~]\s+','',title)
        # remove end dashes
        title=re.sub(r'[\-\~]$','',title)
        title=title.strip()
        return(title)

    # get track index (starting timecode)
    def getIndex(self,line):
        mins=0
        secs=0
        # get the time from the string using getstring - numbers or colon, min 4 chars max 8, valid if includes colon
        time_raw=getString(line,r'[0-9\:]',4,8,':')
        if time_raw == "":
            raise ValueError("Could not get time from line: " + line)
        # split at colon
        time_split=time_raw.split(":")
        # if there's 3 values, last val will be hours - cue format is mins:secs:frames, so multiply hours to mins
        if len(time_split) == 3:
            t=time_split.pop(0)
            mins=int(t) * 60
        t=time_split.pop(0)
        mins=mins+int(t)
        secs=int(time_split[0])
        return(f"{mins:02d}" + ":" + f"{secs:02d}" + ":" + "00")
        

def main(argv):
    # defaults    
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))    

    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        elif opt in ("-i"):
            input_path = Path(arg)

    txtfile=getFile(input_path)
    cue_file=cuefile()
    cue_file.getHeader(input_path) 
    cue_file.getTracks(txtfile)
    cue_file.writeCue(input_path)

if __name__ == "__main__":
    main(sys.argv[1:])