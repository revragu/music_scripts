#!/usr/bin/env python3

import os, re, json, datetime, argparse
from ragu_wikipe import wikipe
from ragu_lang import convCharset, isCJK, isKana, isRoman

def getWikiName(name, language="jp"):
    categories=[
        '*living person*','*存命人物*',
        '*dead person*','*年没*','*亡くなった人物*',
        '*musician*','*音楽家*','*ミュージシャン*',
        '*singer*','*歌手*',
        '*composer*','*作曲家*',
        '*musical group*','*バンド*',
        '*artist*','*アーティスト*',
        '*producer*','*プロデューサー*',
        '*actor*','*俳優*','*声優*'
    ]

    w=wikipe(language=language,categories=categories)
    for n in w.getName(name):
        yield(n)

def getCharset(name,out_dict):
    if isCJK(name) and out_dict['kanji'] == '':
        out_dict['kanji']=name
    if isKana(name) and out_dict['kana'] == '':
        out_dict['kana']=name
    elif isRoman(name) and out_dict['romaji'] == '':
        out_dict['romaji']=name
    return(out_dict)

def checkBreak(out_dict):
    if out_dict['kanji'] != '' and out_dict['romaji'] != '' and out_dict['kana'] != '':
        return(True)
    return(False)


def processContexts(context_list,out_dict):
    for context in context_list:
        if isRoman(context) and out_dict['romaji'] == '':
            out_dict['romaji']=context
        elif isCJK(context,strict=False):
            if isKana(context) and out_dict['kana'] == '':
                out_dict['kana']=context
            elif context.startswith('英語' and out_dict['romaji'] == ''):
                out_dict['romaji']=isRoman(context,sanitize_mode=True)
            elif re.match(r'^[0-9]+年',context):
                pass
            elif out_dict['kanji'] == '':
                out_dict['kanji']=''
        if checkBreak(out_dict):
            break
    
    return(out_dict)
    

def getContextNames(contexts,out_dict):
    context_list=[]
    for context in contexts:
        for separator in [',','、']:
            if separator in context:
                context_list=context.split()
                break
            else:
                context_list=[context]
        
        out_dict=processContexts(context_list,out_dict)
        if checkBreak(out_dict):
            break
    
    return(out_dict)

def getMissingData(out_dict):
    if checkBreak(out_dict):
        return(out_dict)

    if out_dict['kanji'] == '':
        if out_dict['kana'] != '':
            out_dict['kanji']=out_dict['kana']

    if out_dict['kana'] == '':
        if out_dict['kanji'] != '':
            out_dict['kana']=convCharset(out_dict['kanji'],format='hiragana')
        elif out_dict['romaji'] != '':
            out_dict['kana']=convCharset(out_dict['romaji'],format='hiragana')

    if out_dict['kanji'] == '':
        if out_dict['kana'] != '':
            out_dict['kanji']=out_dict['kana']

    if out_dict['romaji'] == '':
        if out_dict['kana'] != '':
            out_dict['romaji']=convCharset(out_dict['kana'],format='hepburn')

    return(out_dict)
    


def matchWikiName(match_name,exact=True):
    out_dict_blank={
        "kanji": '',
        "kana": '',
        "romaji": ''
    }
    for name_result in getWikiName(match_name):
        out_dict=out_dict_blank
        name=name_result[0]
        name_context=name_result[1]
        first_match=name
        if name.replace(' ','') == match_name.replace(''):
            # get main name
            out_dict=getCharset(name,out_dict)
            # get name from contextual names
            out_dict=getContextNames(name_context,out_dict)
            # replace anything missing
            out_dict=getMissingData(out_dict)
            return(out_dict)
    
    if exact == False:
        name=first_match[0]
        name_context=first_match[1]
        out_dict=out_dict_blank
        out_dict=getCharset(name,out_dict)
        out_dict=getContextNames(name_context,out_dict)
        out_dict=getMissingData(out_dict)
        return(out_dict)

def main():
    pass

if __name__ == "__main__":
    main()