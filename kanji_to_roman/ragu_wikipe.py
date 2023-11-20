#!/usr/bin/env python3

import sys, os, re, requests, json, datetime, argparse, ragu_file, ragu_csv, wikipedia
from pathlib import Path
from ragu_lang import convCharset
from ragu_file import readFile
from math import floor

class wikipe():
    def __init__(self,language="en"):
        self.language=language
        self.wikipe=wikipedia
        self.wikipe.set_lang(self.language)
        self.wikipe.set_rate_limiting(True)
        self.results=None
        self.separators=self.getSeparator()

    def getSeparator(self):
        # jp entries introduce the subject with [topic]は、
        if self.language == "jp":
            return(['は、'])
        # en entries introduce the subject with [topic] is/was
        elif self.language == "en":
            return([', is ',', was ',' is ',' was '])
        # no idea what it should be for other languages
        else:
            return([","])

    def search(self,search_term):
        return(self.wikipe.search(search_term))
    
    def getContent(self,search_term):
        self.results=self.wikipe.search(search_term)
        for result in self.results:
            page=self.wikipe.WikipediaPage(title=result)
            yield(page.content)

    def findSeparation(self,string,separator):
        sep_pos=0
        sep_char=separator[sep_pos]
        for i, char in enumerate(string):
            if char == sep_char:
                sep_pos+=1
                if sep_pos > len(separator) - 1:
                    return(True)
                sep_char=separator[sep_pos]
            else:
                return(False)

    def findChunk(self,string,separator):
        sep_point=self.findSeparation(str(string),separator)
        if sep_point == True:
            return(True)

    def getTopicData(self,summary,separators=False):
        if separators == False:
            separators=self.separators

        for i, char in enumerate(summary):
            for separator in separators:
                get_chunk=self.findChunk(summary[i:],separator)
                if get_chunk == True:
                    return(summary[:i])

        return(summary)

    def splitTopicContext(self,topic_data):
        topic_main=topic_data
        topic_context_rev=''
        for parenth_set in [['(',')'],['（','）']]:
            if parenth_set[0] in topic_data:
                if topic_data.endswith(parenth_set[1]):
                    topic_context_rev=(self.getTopicData(summary=topic_data[::-1],separators=parenth_set[0]))[1:].strip()
                    topic_main=topic_data[0:(len(topic_data) - 1) - (len(topic_context_rev) - 1) - 2].strip()

                    break
                else:
                    if ',' in topic_data:
                        topic_data_rev=topic_data[::-1]
                        topic_context_sub_rev=(self.getTopicData(summary=topic_data_rev,separators=','))
                        topic_data_trimmed=(topic_data_rev[len(topic_context_sub_rev):].strip())[1:]

                        topic_main,topic_context_main=self.splitTopicContext(topic_data_trimmed[::-1])
                        topic_context=[topic_context_main,topic_context_sub_rev[::-1].strip()]
                        return(topic_main,topic_context)

        topic_context=(topic_context_rev[::-1])
        return(topic_main,topic_context)

    def matchSummary(self,summary):
        get_chunk=False
        topic_data=''
        topic_context=''

        topic_data=self.getTopicData(summary)
        topic_main,topic_context=self.splitTopicContext(topic_data)
        return(topic_main,topic_context)

    def getName(self,search_term,exact=True):
        best_guess=''
        if self.results == None:
            self.results=self.search(search_term)
        
        if exact == False:
            best_guess=self.results[0]

        for result in self.results:
            try:
                summary=self.wikipe.summary(result,sentences=1)
            except wikipedia.exceptions.PageError as e:
                return(False)
            yield(self.matchSummary(summary))


def cmdParser():
    parser = argparse.ArgumentParser(description='Query wikipedia')
    # Optional argument
    parser.add_argument('-q','--query',type=str,help='Search Query')
    parser.add_argument('-l','--language',type=str,default='en',help='Language to use, defaults to en')
    parser.add_argument('-n','--name',action='store_true',help='Grab name data from the first line of the summary')
    parser.add_argument('-v','--verbose',action='store_true',help='If set, outputs progress')
    args = parser.parse_args()
    global VERBOSE
    VERBOSE=args.verbose
    return(args)



def main(query,lang,name):
    w=wikipe(language=lang)
    if name == True:
        for r in w.getName(query):
            print(r)
    else:
        for result in w.getContent(query):
            print(result)
        


if __name__ == "__main__":
    args=cmdParser()
    main(args.query,args.language,args.name)