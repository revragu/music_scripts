#!/usr/bin/env python3

import sys, os, hashlib
from pathlib import Path
from multiprocessing import Pool



def getHash(file):
    with open(file,'rb') as f:
        data=f.read()
        return(hashlib.md5(data).hexdigest())

def getFiles(input_path):
    output_files=[]
    hash_pairs=[]
    formats=['ape','flac','m4a','mp2','mp3','mp4','mpc','mpg','ogg','opus','tta','wav','wma','wv']
    output_files+=list(Path(input_path).rglob('*'))
    for file in Path(input_path).rglob('*'):
        ext=(os.path.split(file))[1]
        if str(ext).lower() in formats and Path(file).is_file():
            hash=getHash(file)
            hash_pairs.append([hash,file])
            return(hash_pairs)



def main(argv):
    move_to = None
    delete = False
    dry_run = False

    music_dir=Path('m:\music')
    archive_dir=Path('d:\music\!!Archive!!')

    p=Pool(2)
    hashes=p.map(getFiles,[music_dir,archive_dir])

    print(hashes)

if __name__ == "__main__":
    main(sys.argv[1:])