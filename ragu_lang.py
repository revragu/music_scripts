#!/usr/bin/env python3

import sys
from pykakasi import kakasi

# stuff with cjk characters

# if character is CJK, return character. if not, return nothing. 
def isCJK(char,sanitize_mode=False):
    ranges = [
    {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},         # compatibility ideographs
    {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},         # compatibility ideographs
    {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},         # compatibility ideographs
    {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}, # compatibility ideographs
    {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},         # Japanese Hiragana
    {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},         # Japanese Katakana
    {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},         # cjk radicals supplement
    {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
    {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
    {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
    {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
    {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
    {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
    ]
    result=any([range["from"] <= ord(char) <= range["to"] for range in ranges])
    if sanitize_mode == True:
        if result == False:
            return("")
        else:
            return(char)
    
    if result == False:
        return(False)
    else:
        return(True)

# convert japanese character sets between each other
def convCharset(string,format):
    converted_string=""
    string=string.strip()
    # we have to do it character by character, test each character to see if it's CJK, then convert individual characters, because kakasi is buggy with non-alphabet non-CJK chars
    for i, chr in enumerate(string):
        kks=kakasi()
        if isCJK(chr) == "":
            converted_string+=chr
            continue
        conv=kks.convert(chr)
        converted_string+=conv[0][format]

    
    return(converted_string)

def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])