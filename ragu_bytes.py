#!/usr/bin/env python3

import sys
from ragu_file import openFile

# byte operations

# write binary
def writeBin(outputfile,bytes=bytearray()):
    with openFile(outputfile,"wb") as f:
        f.write(bytes)
    return(0)

# read binary
def readBin(inputfile):
    with openFile(inputfile,"rb") as f:
        out_bytes=f.read()
    return(out_bytes)

# read amount of bytes at seek location from file
def readBytes(inputfile='',seek=hex(0x0),amount=-1):
    seek=int(seek,16)
    with openFile(inputfile, "rb") as f:
        f.seek(seek,0)
        out_bytes=f.read(amount)
        return(out_bytes)

# overwrite bytes of file at location_hex (in hex) with bytes in bytes 
def writeBytes(outputfile,inputfile='',location_hex=hex(0x0),bytes=bytearray()):
    with openFile(inputfile,"rb") as f:
        buffer=bytearray(f.read(-1))

    location=int(location_hex,16) + 1

    for byte in bytes:
        buffer[location]=byte
        location-=1

    with openFile(outputfile,"wb") as f:
        f.write(buffer)
    return(0)
    
def main():
    return(0)

if __name__ == "__main__":
    main(sys.argv[1:])