#!/usr/bin/env python3

import sys, json
from ragu_file import openFile

# working with json files

    # list to json
def convertToJson(input_list,conv_ascii=False):      
    try:
        json_output = json.dumps(input_list, indent=4,ensure_ascii=conv_ascii)
        if json_output == "null":
            bad_list = str(input_list)
    except ValueError as e:
        raise ValueError("Could not convert JSON, JSON converter returned null.")
    except TypeError as e:
        raise TypeError("Can't convert input list to JSON, incorrect type")
    except Exception as e:
        raise Exception(f'Unhandled Exception converting list to JSON: {e}')
    return(json_output)

# convert json to list
def convertFromJson(input_json):
    try:
        output_list = json.loads(input_json)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("Can't convert JSON to list from input json.")
    except Exception as e:
        raise Exception(f'Unhandled Exception converting JSON to list: {e}')

    return(output_list)

# print list as json
def printJson(input_list,conv_ascii=False):
    print(convertToJson(input_list,indent=4,ensure_ascii=conv_ascii))
    return(0)


# write json
def writeJson(input_obj,filename,conv_ascii=False):
    with openFile(filename, 'w', encoding='utf-8') as outfile:
        json.dump(input_obj,outfile,ensure_ascii=conv_ascii,indent=4)
    return(0)


def main():
    return(0)

if __name__ == "__main__":
    main(sys.argv[1:])