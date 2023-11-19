#!/usr/bin/env python3

import sys
from pykakasi import kakasi

# stuff with cjk characters

# if character is CJK, return character. if not, return nothing. 
def checkKanaChar(char):
    ranges = [
    {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},         # Japanese Hiragana
    {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")}         # Japanese Katakana
    ]
    result=any([range["from"] <= ord(char) <= range["to"] for range in ranges])
    if result == False:
        return(False)
    else:
        return(True)

# verifies string has kana and no kanji
def isKana(string):
    kana_chrs=[]
    for char in string:
        if checkCJKChar(char) == True:
            if checkKanaChar(char) == True:
                kana_chrs.append(char)
            else:
                return(False)
    if len(kana_chrs) > 0:
        return(True)
              
    return(False)


def checkCJKChar(char):
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
    if result == False:
        return(False)
    else:
        return(True)

# check if string is cjk. 
def isCJK(string,sanitize_mode=False):
    sanitize_str=''
    for chr in string:
        if checkCJKChar(chr) == True:
            if sanitize_mode == True:
                sanitize_str+=chr
            else:
                return(True)
    
    if sanitize_mode == False:
        return(False)

    if len(sanitize_str) > 0:
        return(sanitize_str)
    else:
        return(' ')


            



# convert japanese character sets between each other
def convCharset(string,format):
    converted_string=''
    mode='none'
    curr_char=''
    char_list=[]
    curr_run=''
    for char in string:
        if isCJK(char):
            curr_char='kanji'
            if isKana(char):
                curr_char='kana'
        else:
            curr_char='non_jp'
        
        if mode != curr_char:
            if len(curr_run) > 0:
                char_list.append(curr_run)
                curr_run=''
        mode=curr_char
        curr_run+=char

    if len(curr_run) > 0:
        char_list.append(curr_run)

    kks=kakasi()
    for run in char_list:

        if isCJK(run):
            conv=kks.convert(run)
            for iter in conv:
                if format in iter.keys():
                    converted_string+=iter[format]
                else:
                    converted_string+=iter
        else:
            converted_string+=run


    return(converted_string)


    # converted_string=""
    # string=string.strip()
    # special_char=''
    # # we have to do it character by character, test each character to see if it's CJK, then convert individual characters, because kakasi is buggy with non-alphabet non-CJK chars
    # for i, char in enumerate(string):
    #     kks=kakasi()
    #     if isCJK(char) == False:
    #         converted_string+=char
    #         continue
        
    #     sokuon=["ッ","っ"]
    #     chouonpu_digraphs=['ー','ょ','ゅ','ゃ','ョ','ュ','ャ','ぁ','ぅ','ぇ','ぃ','ぉ','ァ','ィ','ゥ','ェ','ォ']

    #     # ugly hack for chouonpu and digraphs
    #     # since sokuon modify the sound of the next character, they need to be added in the next iteration, so skip the current and add them with the next char
    #     # chouonpu and the other digraphs modify the previous character, so grab them from the next iteration and add them to the current character, then skip the next iteration
    #     if special_char in sokuon:
    #         chr=special_char + char
    #         special_char=''
    #     elif special_char in chouonpu_digraphs:
    #         special_char=''
    #         continue
    #     if char in sokuon:
    #         if i < len(string) - 1:
    #             # store sokuon for next iteration
    #             special_char=char
    #             continue
    #     elif i < len(string) - 1 and string[i + 1] in chouonpu_digraphs:
    #         char=char + string[i + 1]
    #         special_char=string[i + 1]



    #     conv=kks.convert(char)
    #     if format in conv[0].keys():
    #         converted_string+=conv[0][format]
    #     else:
    #         converted_string+=conv[0]

    
    # return(converted_string)

def main(argv):
    pass


if __name__ == "__main__":
    main(sys.argv[1:])