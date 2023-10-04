#!/usr/bin/env python3

import sys, csv, json, re, os

# file stuff

# error handler
def handleError(e, error_type, bad_input = '', bad_output = ''):
    error_class = re.sub(r'<class \'(.*)\'>',r'\1',str(e.__class__))
    print(error_class)
    error_tuple = e.args
    error_string = ""
    for i in error_tuple:
        error_string =(error_string + ' '  + i).strip()

    try:
        bad_input_str = str(bad_input)
    except:
        bad_input_str = "(could not parse incorrect type)"
    
    try:
        bad_output_str = str(bad_output)
    except:
        bad_output_str = "(could not parse incorrect data)"
    
    if error_type == "exception":
        raise Exception("Unhandled Exception: " + error_class + " - " + error_string)
    elif error_type == "json_converter_null":
        raise ValueError("Could not convert JSON, JSON converter returned null." +  + "Input list: " + os.linesep + bad_input)
    elif error_type == "json_converter_bad_type":
        raise TypeError("Can't convert input list to JSON, incorrect type: " + bad_input_str + os.linesep + "Input list: " + os.linesep + bad_output_str)

# convert list to json
def convertToJson(input_list):
    try:
        json_output = json.dumps(input_list, indent=4)
        if json_output == "null":
            bad_list = str(input_list)      
    except ValueError as e:
        handleError(e, "json_converter_null", input_list)
    except TypeError as e:
        handleError(e, "json_converter_bad_type", type(input_list), input_list)
    except Exception as e:
        handleError(e, "exception")
    return json_output

# convert json to list
def convertFromJson(input_json):
    try:
        list_output = json.loads(input_json)
    except json.decoder.JSONDecodeError as e:
        bad_json = str(input_json)
        raise ValueError("Can't convert JSON to list from input json: " + os.linesep + bad_json)
    except Exception as e:
        raise(e)
    return list_output

# print list as json
def printJson(input_list):
    # see if it can be converted into a list, which will verify that it's valid json    
    try:
        json_out = json.dumps(input_list, indent=4,ensure_ascii=True)
        convertFromJson(json_out)
    except Exception as e:
        raise(e)
    print(json_out)


def writeJson(input_obj,filename):
    try:
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(input_obj,outfile,ensure_ascii=False,indent=4)
    except Exception as e:
        raise(e)


# read file into string
def readFile(input_file,enc_format="utf8"):
    try:
        with open(input_file, 'r', encoding=enc_format) as open_file:
            output_file=open_file.read()
    except (FileNotFoundError, TypeError) as e:
        bad_input = str(input_file)
        raise FileNotFoundError("File does not exist: " + bad_input)
    except PermissionError as e:
        raise PermissionError("Permission denied: " + input_file)
    except Exception as e:
        raise(e)
    return output_file


def readBytes(inputfile,seek=hex(0x0),amount=-1):
    seek=int(seek,16)
    with open(inputfile, "rb") as f:
        f.seek(seek,0)
        out_bytes=f.read(amount)
        return(out_bytes)

# read amount number of bytes at seek location from file
def readBytesfromFile(inputfile,seek=hex(0x0),amount=-1):
    seek=int(seek,16)
    with open(inputfile, "rb") as f:
        f.seek(seek,0)
        out_bytes=f.read(amount)
        return(out_bytes)


# overwrite bytes of file at location_hex (in hex) with bytes in bytes 
def writeBytes(inputfile,outputfile,location_hex=hex(0x0),bytes=bytearray()):
    with open(inputfile,"rb") as f:
        buffer=bytearray(f.read(-1))

    location=int(location_hex,16) + 1

    for byte in bytes:
        buffer[location]=byte
        location-=1

    with open(outputfile,"wb") as f:
        f.write(buffer)

def dictListToCsvList(input_dict):
    output_list=[]
    header=[]
    for idx, row in enumerate(input_dict):
        row_list=[]
        if idx == 0:
            for k,v in row.items():
                header.append(k)
            output_list.append(header)

        for heading in header:
            row_list.append(row[heading])
        output_list.append(row_list)
    return(output_list)

    



def readCsvtoDicts(input_file,delim=','):
    csv_file=(readFile(input_file)).split('\n')
    csv_stripped=[x for x in csv_file if x]
    header=[]
    list_output=[]
    for idx, line in enumerate(csv_stripped):
        row=line.split(delim)
        if idx == 0:
            for heading in row:
                header.append(heading.strip())
        else:
            row_dict={}
            for i in range(0,len(header)):
                row_dict[header[i]]=row[i]
            list_output.append(row_dict)
    
    return(list_output)


def writeDictstoCsv(input_dict,filename,delim=',',overwrite=False):
    try:
        csv_list=dictListToCsvList(input_dict)
    except Exception as err:
        raise(Exception,"Something went wrong converting dicts to csv format: "+err)

    writeCsv(filename,csv_list[0],csv_list[1:],delim,overwrite)


# reads csv to list of dicts
def readCsv(input_file,delim=','):
    csv_output = []
    header = []
    try:
        with open(input_file, mode='r', newline='') as csv_file:
            csv_input = csv.reader(csv_file, delimiter=delim)
            for idx, row in enumerate(csv_input):
                if idx == 0:
                    for heading in row:
                        header.append(heading)
                else:
                    current_dict={}
                    for idx, item in enumerate(row):
                        current_dict[header[idx]] = item
                    
                    
                    csv_output.append(current_dict)
        return csv_output
    except FileNotFoundError as e:
        raise(e)
    except IndexError as e:
        raise IndexError("File",input_file,"is not a valid CSV file")
    except PermissionError as e:
            raise PermissionError("Permission denied: " + input_file)

# writes list of dicts to csv
def writeCsv(filename, header, output_list, delim=',', overwrite=False):
    try:
        if os.path.exists(filename) == True:
            if overwrite == False:
                raise FileExistsError(filename + " already exists, can't create csv")
            else:
                os.remove(filename)
        with open(filename, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter = delim)
            csv_writer.writerow(header)
        
            for line in output_list:
                csv_writer.writerow(line)
        
        return 0
            
    except FileExistsError as e:
        raise(e)
    except Exception as e:
        raise Exception(e)
     

# renamer
def fileRenamer(filename):
    new_filename = filename
    for i in range(1,999):
        if os.path.exists(new_filename):
            istr = str(i)
            file_split = filename.split('.')
            if isinstance(file_split,list) and len(file_split) >= 2:
                file_split[-2] = file_split[-2] + '-' + istr
            
            new_filename = ""
            for idx, split in enumerate(file_split):
                if idx == 0:
                    new_filename = split
                else:
                    new_filename = new_filename + '.' + split
        else:
            return new_filename
    
    raise FileExistsError("Could not rename " + filename + ", tried 999 times")

def main():
    pass

if __name__ == "__main__":
    main(sys.argv[1:])