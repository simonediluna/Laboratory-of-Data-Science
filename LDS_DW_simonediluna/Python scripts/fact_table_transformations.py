# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11
    
Programme goals:
    * Rename attribute: sales_uds, time_code.
    * Drop attributes: Id, gpu_code, ram_code.
    * Add cost attribute.
    * Cast cpu_code type to int.
    * Remove missing values in cpu_code.
"""

import csv
import random
import os


# Function definitions
def assign_loc(path: str) -> str:
    """
    Check whether the input path already exists. If so, search for an 
    available name in the current destination. In both cases, return the path.
    """
    i = 1
    name, ext = path.rsplit('.', 1)
    while os.path.exists(path):
        path =  f"{name}_({i}).{ext}"
        i += 1
    return path

def vars_exist(path: str, col_names: list[str], sep=","):
    """
    Check the existence of the input attributes
    """
    with open(path) as file:
        header = set(file.readline().split(sep))
        for col in col_names:
            if col not in header:
                raise NameError(f'{col} is not an attribute')

def rename_attrs(
        path: str, 
        to_rename: dict[str, str], 
        inplace=False, 
        sep: str = ","
    ) -> str:
    """
    Rename the attributes of the file and return the path.
    
    Parameters
    ----------
        path: The location of the file.
        
        to_rename: A dict containing ( old_name, new_name ) pairs.
        
        inplace: If True, the file with the new header overwrite the
            content of the file in path. On the other hand, if False, both
            files are preserved.
            
        sep: the separator used in the csv file.
    """
    
    new_path = assign_loc(path)
    with open(path) as ifile, open(new_path, "w") as ofile:
        
        # Create new header
        old_header = ifile.readline().removesuffix('\n')
        new_header = ''
        for var in old_header.split(sep):
            if var in to_rename:
                new_header += to_rename[var] + sep
            else:
                new_header += var + sep
        new_header = new_header[:-1] + '\n'
        
        # Write new file
        ofile.write(new_header)
        for line in ifile:
            ofile.write(line)
    
    # replace content of path with that of new path    
    if inplace:
        os.replace(new_path, path)
        return path
    return new_path
        
def compute_cost(
        revenue: str, 
        markup_range: tuple[float, float] = (0.15, 0.4)
    ) -> float:
    """
    Estimate the cost by means of a markup drawn at random from a uniform 
    distribution and bound to take a value in the input range. This function 
    was designed to be used as an argument in the modify_table function.
    
    Parameters
    ----------
        revenue: The ravenue of the fact as a string.
        
        markup_range: The range (min, max) of possible values that the markup
            can assume.
    """
    rnd = random.random()
    delta = markup_range[1] - markup_range[0]
    markup = rnd * delta + markup_range[0]
    return float(revenue) / (1 + markup)

def modify_table(
        path: str, 
        to_drop: set[str] = set(),
        to_add: dict[str, tuple] = dict(),
        to_cast: dict[str, type] = dict(),
        drop_lines: set[str] = set(),
        missing_value: str = "",
        inplace: bool = False
    ) -> str:
    """
    Apply different transformations to the file located in path. These 
    transformations are applied with a unique iteration over the file.
    At the end, return the path of the new table.
    
    Parameters
    ----------
        to_drop: Attribute or list of attribute to remove.
        
        to_add: A dictionary where the key is the attribute to add to the 
            table and the value is a tuple containg the function to apply and
            an iterable object with the parameters to pass to the function.
            
        to_cast: A dictionary storing pairs of attribute and cast type to apply.
        
        drop_lines: A set of attributes for which, in the case of missing
            values, the 'remove row' policy is adopted.
        
        missing_value: Form in which missing values occur.
        
        inplace: If True, the original file is replaced with the new one.
    """
    
    if not any((to_drop, to_add, to_cast, drop_lines)):
        return

    # Check the existence of the input attributes
    to_check = []
    for obj in (to_drop, to_cast, drop_lines):
        if obj:
            if isinstance(obj, dict):
                to_check += list(obj.keys())
            elif isinstance(obj, set):
                to_check += list(obj)
            else:
                raise TypeError
    vars_exist(path, to_check)
    
    # Core 
    ofile_path = assign_loc(path)
    with (
        open(path, newline="") as ifile, 
        open(ofile_path, "w", newline="") as ofile
    ):
        reader = csv.DictReader(ifile)
        
        # Define the new header
        to_keep = []
        header = []
        for col in reader.fieldnames:
            if col not in to_drop:
                to_keep.append(col)
                header.append(col)
        if to_add:
            header.extend(list(to_add.keys()))
        
        # Write the new file
        writer = csv.DictWriter(ofile, header, extrasaction='ignore')
        writer.writeheader()
        for row in reader:
            for col in to_keep:
                if col in drop_lines and row[col] == missing_value:
                    break  # Skip line
            
            # If break did not occur, apply the required transformations.
            else:
                if to_add:
                    for new_var, dct in to_add.items():
                        d = iter(dct.items())
                        _, func = next(d)
                        _, var = next(d)
                        kwargs = dict(d)
                        row[new_var] = str(func(row[var], **kwargs))
                if to_cast:
                    for var, tp in to_cast.items():
                        row[var] = str(tp(float(row[var])))
                    
                writer.writerow(row)
                
    if inplace:
        os.replace(ofile_path, path)
        return path
    return ofile_path
                

# Main program
if __name__ == "__main__":

    # Set the random seed for the compute_cost function
    random.seed(42)
    
    # Get the location of the file from the user
    loc = input("Enter the path to the .csv file: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
    
    # Define function arguments
    to_rename = {"sales_uds": "sales_usd", "time_code": "time_id"} 
    to_drop = set("Id gpu_code ram_code".split())
    to_add = {"cost": {"func": compute_cost, "attr": "sales_usd"}}
    to_cast = {"cpu_code": int}
    drop_lines = {"cpu_code"}
    
    # Run functions
    loc = rename_attrs(loc, to_rename)
    modify_table(loc, to_drop, to_add, to_cast, drop_lines, inplace=True)
                    
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                