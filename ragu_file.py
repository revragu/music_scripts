#!/usr/bin/env python3

import sys

# file operations

def openFile(file='',method='r',encoding='utf-8',newline="\n"):
    try:
        if 'b' not in method:
            return(open(file,method,encoding=encoding,newline=newline))
        else:
            return(open(file, method))
    except (FileNotFoundError, TypeError) as e:
        raise FileNotFoundError(f"File does not exist: {str(file)}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied for {str(file)} with method {method} and encoding {encoding}")
    except Exception as e:
        raise Exception(f"Could not open file {str(file)} with method {method} and encoding {encoding}: " + e)

# read file into string
def readFile(input_file,enc_format="utf-8"):
    with openFile(input_file, 'r', encoding=enc_format) as open_file:
        output_str=open_file.read()
    return(output_str)

# read file into list
def readFileToList(input_file='',enc_format="utf-8"):
    with openFile(input_file, 'r', encoding=enc_format) as open_file:
        output_list=open_file.readlines()
    return(output_list)

# Convert list of dicts to 3 dimensional list
def convListdicts(input_list):
    output_list=[]
    header=list(input_list[0].keys())
    output_list.append(header)
    for row in input_list:
        row_list=[]
        for heading in header:
            row_list.append(row[heading])
        output_list.append(row_list)
    return(output_list)
    
def main():
    return(0)

if __name__ == "__main__":
    main(sys.argv[1:])