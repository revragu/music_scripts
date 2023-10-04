#!/usr/bin/env python3

import sys, csv, json, re, os


def bytesum(input_bytes):
    all_bytes=bytearray(input_bytes)
    sum=0
    for b in all_bytes:
        sum+=b
    return(sum)



def clearBits(input_byte,mask):
    # byte errors
    if isinstance(input_byte,bytes):
        input_byte=int.from_bytes(input_byte,"little")

    if not isinstance(input_byte,int):
        try:
            input_byte=int(input_byte)
        except:
            raise TypeError("Cannot convert "+input_byte+" to int")
    
    if input_byte > 255:
        raise ValueError(input_byte + " must be a value between 0 and 255")

    # mask errors
    if isinstance(mask,int) != True:
        raise TypeError("Mask must be integer")

    if mask > 255 or mask < 1:
        raise ValueError("Mask must be an 8 bit value between 1 and 255")
    
    # abjunction
    # 1,1=0
    # 1,0=1
    # 0,1=0
    # 0,0=0
    return(input_byte & ~mask)


# count bits needed to represent value
def countBits(a):
    bits=1
    val=1
    while val <= a:
        bits+=1
        val=val << 1
    return(bits)


# count needed number of bytes to store value. if negative, use signed value. signed value can be forced.
def countBytes(a,signed=False):
    start_val=255
    count=1
    if a < 0:
        start_val=127
        signed=True
    if signed == True and a < 0:
        while a + start_val < 0:
            start_val*=2
            count+=1
    else:
        while a - start_val > 0:
            start_val*=2
            count+=1
    return(count)


# determine if input is an integer, convert to bytes
def convInts(a,endian='little'):
    if isinstance(a,int):
        num_of_bytes=countBytes(a)
        return(a.to_bytes(num_of_bytes,endian))
    else:
        return(a)

# logical operations using bytes as inputs. if ints are used, will convert to bytes
def byteAnd(a,b,endian='little'):
    a = convInts(a,endian)
    b = convInts(b,endian)
    result_int = int.from_bytes(a, byteorder=endian) & int.from_bytes(b, byteorder=endian)
    return result_int.to_bytes(max(len(a), len(b)), byteorder=endian)

def byteOr(a,b,endian='little'):
    a = convInts(a,endian)
    b = convInts(b,endian)
    result_int = int.from_bytes(a, byteorder=endian) | int.from_bytes(b, byteorder=endian)
    return result_int.to_bytes(max(len(a), len(b)), byteorder=endian)

def byteXor(a,b,endian='little'):
    a = convInts(a,endian)
    b = convInts(b,endian)
    result_int = int.from_bytes(a, byteorder=endian) ^ int.from_bytes(b, byteorder=endian)
    return result_int.to_bytes(max(len(a), len(b)), byteorder=endian)

def main(argv):
    print(clearBits(85,12))

if __name__ == "__main__":
    main(sys.argv[1:])