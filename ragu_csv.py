#!/usr/bin/env python3

import sys, csv
from ragu_file import openFile,convListdicts

# csv operations

# reads csv. if there are headers, read to list of dicts. if no headers, list of lists
def readCsv(input_file,header=True,delim=','):
    csv_output = []
    try:
        with openFile(input_file, 'r') as csv_file:
            csv_input = csv.reader(csv_file, delimiter=delim)
            if header == True:
                header=csv_input[0]
                current_dict={}
                for row in csv_input:
                    current_dict={}
                    for idx, item in enumerate(row):
                        current_dict[header[idx]] = item
                    csv_output.append(current_dict)

            else:
                for row in csv_input:
                    csv_output.append(row)

        return csv_output
    except IndexError as e:
        raise IndexError(f'File {input_file} is not a valid CSV file')


# writes list to csv
def writeCsv(filename, output_list, header=[], delim=',', overwrite=False):
    if type(overwrite) == bool:
        if overwrite == True:
            writemode='a'
        else:
            writemode='w'

    print(header)
    with openFile(filename, writemode, newline='', encoding="utf-8") as csv_file:
        if len(header) > 0:
            csv_writer = csv.writer(csv_file, delimiter = delim)
            csv_writer.writerow(header)
        
        for line in output_list:
            csv_writer.writerow(line)
    return 0

# converts list of dicts to list of lists for csv conversion, then writes the csv
def writeDictstoCsv(input_dict,filename,delim=',',overwrite=False):
    try:
        csv_list=convListdicts(input_dict)
    except Exception as err:
        raise Exception(f'Something went wrong converting dicts to csv format: {err}')

    writeCsv(filename,csv_list[1:],csv_list[0],delim,overwrite)
    
def main():
    return(0)

if __name__ == "__main__":
    main(sys.argv[1:])