#!/usr/bin/env python3

import sys, getopt
from yuuchuub import youtube_search

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    pass


def main(argv):
    channel=None
    req=None
    pipe=False
    try:
        opts, args = getopt.getopt(argv,"hr:c:i:p")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
    if len(opts) == 0:
        pipe=True

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt == "-i":
            input_file=arg
        elif opt == "-p":
            pipe=True
        elif opt == "-p":
            channel=arg
        
    search=youtube_search()

    for req in sys.stdin:
        search.search(request=req,channelId=channel)
        print(search.getDate())

if __name__ == "__main__":
    main(sys.argv[1:])