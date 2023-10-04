#!/usr/bin/env python3

from distutils.errors import UnknownFileError
import sys, re, os, getopt, ragu_file
from pathlib import Path
from pydub import AudioSegment
import mutagen
from mutagen import File as audioFile
from random import randrange

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass

class getTags:
    def __init__(self,path=None):
        self.path=path
        self.audio_file = None

    def getPath(self,path):
        if path != None:
            return(path)
        else:
            return(self.path)

    def plainText(self,path=None):
        self.path=self.getPath(path)
        self.audio_file=audioFile(self.path)
        tags=set(self.audio_file.tags)
        tags=set([str(self.audio_file.tags[tag]) for tag in self.audio_file.tags])
        return(tags)


def main(argv):
    # defaults    
    try:
        opts, args = getopt.getopt(argv,"hi:",["help","input="])
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
        

    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit(0)
        elif opt in ("-i","--input"):
            path = Path(arg)
    
    
    tags=getTags(path)
    print(tags.plainText())
        
        



if __name__ == "__main__":
    main(sys.argv[1:])