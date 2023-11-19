#!/usr/bin/env python3

import sys, re, os, getopt, ragu_file
from googleapiclient.discovery import build

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass


class youtube_search:
    def __init__(self):
        self.devkey=self.__getDevkey__()
        self.response=None
        self.channelId=None

    def __getDevkey__(self):
        with open('devkey.txt','r') as f:
            return(f.readline())
        
    def search(self,request,channelId=None):
        self.channelId=channelId
        with build('youtube','v3',developerKey=self.devkey) as service:
            self.response=service.search().list(
                part='id,snippet',
                maxResults=10,
                q=request
            ).execute()

    def getDate(self):
        date=[r['snippet']['publishedAt'] for r in self.response['items'] if self.channelId == None or r['snippet']['channelId'] == self.channelId][0]
        return(date[0:4])


def main(argv):
    channel=None
    req=None

    try:
        opts, args = getopt.getopt(argv,"hr:c:")
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
        elif opt == "-r":
            req=arg + ',snippet'
        elif opt == "-c":
            channel=arg

    search=youtube_search()
    search.search(request=req,channelId=channel)
    print(search.getDate())


if __name__ == "__main__":
    main(sys.argv[1:])