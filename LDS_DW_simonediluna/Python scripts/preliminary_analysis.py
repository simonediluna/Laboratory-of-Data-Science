# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

This script was used to check certain assumptions and perform some tests 
before building the tables in SQL Server.
"""
import csv
import os


# "Global" variables
missing = {"", " ", "?", "-", "nan", "na", "null", "unknown", "empty", 
           "missing", "no value"}


# Function definitions
def is_qualitative(string: str) -> bool:
    """
    Check if the input string is qualitative (not int or float).
    """
    try:
        float(string)
        return False
    except ValueError:
        return True
    
    
def check_types_and_missing(csv_path: str) -> tuple[dict, dict, dict]:
    """
    Ascertain the type of each attribute and the presence of missing values.
    Return a 3-tuple composed by:
        1. A dict containing attribute: type pairs.
        2. A dict storing for each attribute the set containing the types of
           missing values found.
        3. A dict showing for each attribute the number of missing values found.
    """
    with open(csv_path, newline='') as file:
        reader = csv.DictReader(file)
        types = dict.fromkeys(reader.fieldnames, True) # str, F(float), T(int)
        miss_vals = {var: set() for var in reader.fieldnames}
        n_miss_vals = dict.fromkeys(reader.fieldnames, 0)

        for row in reader:
            for var in reader.fieldnames:

                # Missing value found.
                if row[var].casefold() in missing:
                    miss_vals[var].add(row[var])
                    n_miss_vals[var] += 1

                # Type ascertained. The attribute has str type for sure.
                elif is_qualitative(row[var]):
                    types[var] = str

                # Checks whether the type of the quantitative 
                # attribute is int or float.
                else:
                    types[var] &= row[var].isnumeric()
         
        # Replace 0 and 1 with float and int, respectively
        for var in reader.fieldnames:
            if types[var] == str:
                continue
            elif types[var]: 
               types[var] = int
            else:
                types[var] = float
                
    return types, miss_vals, n_miss_vals


def find_boundaries(csv_path: str, types: dict) -> tuple[dict, dict]:
    """ 
    For each attribute, if qualitative, determine the minimum and maximum 
    length, if numeric determine the minimum and maximum value. 
    For qualitative attributes, also determine the encoding type.
    """
    with open(csv_path, newline='') as file:
        reader = csv.DictReader(file)
        boundaries = {var: [float("inf"), float("-inf")] 
                      for var in reader.fieldnames} # Attr: [min, max] len or val
        str_vars = [var for (var, tp) in types.items() if tp == str]
        encodings = dict.fromkeys(str_vars, True)  # False unicode, True ascii 
        
        for row in reader:
            for var in reader.fieldnames:
                if row[var].casefold() not in missing:
                    if types[var] == str:
                        # Determine max/min length for non numeric attributes
                        boundaries[var][1] = max(boundaries[var][1], 
                                                 len(row[var]))
                        boundaries[var][0] = min(boundaries[var][0], 
                                                 len(row[var]))
                        encodings[var] &= row[var].isascii()
                    else:
                        # Determine max/min value for numeric attributes
                        boundaries[var][1] = max(boundaries[var][1], 
                                                 types[var](row[var]))
                        boundaries[var][0] = min(boundaries[var][0], 
                                                 types[var](row[var]))               
            
        for var in str_vars:
            if encodings[var]:
                encodings[var] = 'ASCII'
            else:
                encodings[var] = 'Unicode'
        
    return boundaries, encodings


def produce_report(paths):
    report = []
    for path in paths:
        tab_name = path.split("\\")[-1].removesuffix(".csv")
        types, miss_vals, n_miss_vals = check_types_and_missing(path)
        boundaries, encodings = find_boundaries(path, types)
        
        # Fill the output report
        report += [f"{tab_name:*^50}"]
        for attr, tp in types.items():
            report += [f"{attr}:\n\ttype: {tp},"]
            if tp == str:
                report += [f"\tmin length: {boundaries[attr][0]},\n"
                            f"\tmax length: {boundaries[attr][1]},\n"
                            f"\tstring encoding: {encodings[attr]},"]
            else:
                report += [f"\tmin value: {boundaries[attr][0]},\n" 
                            f"\tmax value: {boundaries[attr][1]},"]
            report += [f"\tmissing values (encodings): {miss_vals[attr]},\n"
                       f"\t# missing values: {n_miss_vals[attr]}\n"]
        
    # Print the report and write it on a file
    report = "\n".join(report)
    print(report)
    opath = os.path.dirname(paths[0]) + r"\preliminary_analysis_report.txt"
    with open(opath, "w") as file:
        file.write(report)
        

# Main program
if __name__ == "__main__":
    
    # Get the location of the file/s from the user and produce the report.
    loc = input("Enter the path to either the .csv file " 
                 "or the folder containing the .csv files: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
    if os.path.isfile(loc):
        produce_report([loc])
    else:
        csv_files = [loc + "\\" + file_name for file_name in os.listdir(loc) 
                     if file_name.endswith(".csv")]
        produce_report(csv_files)

