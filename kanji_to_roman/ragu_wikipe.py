#!/usr/bin/env python3

import argparse, wikipedia, re

class wikipe():
    def __init__(self,language="en",categories=None):
        self.categories=self.parseInputCategories(categories)
        self.language=language
        self.wikipe=wikipedia
        self.wikipe.set_lang(self.language)
        self.wikipe.set_rate_limiting(True)
        self.results=None
        self.separators=self.getSeparator()


    def parseInputCategories(self,categories):
        results=[]
        if type(categories) == list:
            for cat in categories:
                results.append(cat.lower())
            return(results)
        if type(categories) != None:
            raise ValueError('Category must be None or a list')


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

    def search(self,search_term,max_results=10,exact=True):
        suggest=not exact
        search=self.wikipe.search(search_term,max_results,suggestion=suggest)
        results=[]
        for s in search:
            if type(s) == list:
                for t in s:
                    yield(self.getPage(t))
            else:
                yield(self.getPage(s))

    def getPage(self,search_result):
        try:
            return(self.wikipe.WikipediaPage(title=search_result))
        except wikipedia.exceptions.DisambiguationError:
            return(False)
        except ValueError:
            return(False)
        except Exception as e:
            raise Exception(f"Unhandled exception of type {type(e)}: {str(e)}")

    
    def getContent(self,search_term):
        self.results=self.wikipe.search(search_term)
        for result in self.results:
            if type(result) == wikipedia.WikipediaPage:
                yield(result.content)


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
        topic_context=''
        for parenth_set in [['(',')'],['（','）']]:
            if parenth_set[0] in topic_data:
                if topic_data.endswith(parenth_set[1]):
                    topic_context=(((self.getTopicData(summary=topic_data[::-1],separators=parenth_set[0])).strip())[1:])[::-1]
                    topic_main=(((topic_data[0:(len(topic_data)) - (len(topic_context))].strip())[::-1])[2:])[::-1]
                    break
                else:
                    if ',' in topic_data:
                        topic_data_rev=topic_data[::-1]
                        topic_context_sub_rev=(self.getTopicData(summary=topic_data_rev,separators=','))
                        topic_data_trimmed=(topic_data_rev[len(topic_context_sub_rev):].strip())[1:]

                        topic_main,topic_context_main=self.splitTopicContext((topic_data_trimmed[::-1]).strip())
                        topic_context=[topic_context_main[0].strip(),topic_context_sub_rev[::-1].strip()]
                        break
        if type(topic_context) != list:
            topic_context=[topic_context]
        return(topic_main.strip(),topic_context)

    def matchSummary(self,summary):
        get_chunk=False
        topic_data=''
        topic_context=''

        topic_data=self.getTopicData(summary)
        topic_main,topic_context=self.splitTopicContext(topic_data.strip())
        return(topic_main,topic_context)

    def getCategories(self,search_result):
        return([c.lower() for c in search_result.categories])

    def matchCategories(self,search_result):
        try:
            page_cats=self.getCategories(search_result)
        except:
            page_cats=''
        for category in page_cats:
            if category in self.categories:
                return(True)
            else:
                for c in self.categories:
                    regex_cat=c.replace('*','.*')
                    if '*' in c and re.match(rf'^{regex_cat}$',category):
                        return(True)
        return(False)
        


    def getName(self,search_term,exact=True):
        exact=False
        if self.results != None:
            yield(False)

        for result in self.search(search_term,max_results=10,exact=exact):
            try:
                if type(result) == wikipedia.WikipediaPage and (len(self.categories) == 0 or self.matchCategories(result)):
                    summary=result.summary.split("\n")[0]
                else:
                    continue
            except wikipedia.exceptions.PageError as e:
                yield(False)
            except Exception as e:
                raise Exception(f"Unhandled exception of type {type(e)}: {str(e)}")
            yield(self.matchSummary(summary))



def cmdParser():
    parser = argparse.ArgumentParser(description='Query wikipedia')
    # Optional argument
    parser.add_argument('-q','--query',type=str,help='Search Query')
    parser.add_argument('-l','--language',type=str,default='en',help='Language to use, defaults to en')
    parser.add_argument('-n','--name',action='store_true',help='Grab name data from the first line of the summary')
    parser.add_argument('-c','--categories',type=str,default=None,help='Comma separated list of valid categories. * for wildcard')
    parser.add_argument('-v','--verbose',action='store_true',help='If set, outputs progress')
    args = parser.parse_args()
    global VERBOSE
    VERBOSE=args.verbose
    return(args)



def main(query,lang,name,cat):
    if type(cat) == str:
        cat=cat.split(",")
    w=wikipe(language=lang,categories=cat)
    if name == True:
        for r in w.getName(query):
            print(r)
    else:
        for result in w.getContent(query):
            print(result)
        


if __name__ == "__main__":
    args=cmdParser()
    main(args.query,args.language,args.name,args.categories)