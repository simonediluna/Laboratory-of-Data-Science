# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

Programme goals:
    * Rename attribute: name.
    * Remove prefix string from socket.
    * Enforce the FD between socket and brand.
    * Fill the missing value found in the preliminary analysis.
    * Fix inconsistencies.
"""

import csv
import os
from fact_table_transformations import rename_attrs, assign_loc
from collections.abc import Iterable

def check_fdependency(
        path: str, 
        domain: Iterable[str], 
        codomain: Iterable[str]
    ) -> bool:
    """
    Check the functional dependency between the two sets 
    of attributes passed in input, i.e., domain -> codomain.
    """
    if isinstance(domain, str):
        domain = [domain]
    if isinstance(codomain, str):
        codomain = [codomain]

    with open(path, newline='') as file:
        reader = csv.DictReader(file)
        groupings = {}

        for row in reader:
            lhs = tuple([row[attr] for attr in domain]) # left hand side
            rhd = tuple([row[attr] for attr in codomain]) #right hand side
            if lhs in groupings:
                groupings[lhs].add(rhd)
            else:
                groupings[lhs] = {rhd}

        ans = True  
        for lhs, rhd in groupings.items():
            if len(rhd) > 1:
                ans = False
                print(f'{lhs}: {rhd}')
        return ans



if __name__ == "__main__":
    
    # Get the location of the file from the user
    loc = input("Enter the path to the .csv file: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
    
    # Assess the functional dependency between socket and brand.
    # msg = "The functional dependency is not respected."
    # assert check_fdependency(loc, 'socket', 'brand'), msg

    # Rename attribute "name" in "cpu_name"
    to_rename = {"name": "cpu_name"}
    loc = rename_attrs(loc, to_rename)
    
    to_fix = {
        'series': {
            'Unknown': 'Amd E-Series', 
            'Amd 2650': 'Amd Sempron',
            'Amd 3850': 'Amd Sempron', 
            'Amd 5150': 'Amd Athlon', 
            'Amd 5350': 'Amd Athlon', 
            'Amd E2-3200':'Amd E-Series',
            'Amd E-Series E-450': 'Amd E-Series'
        },
        'cpu_name': {
            'Amd E-Series E-450': 'Amd E-450', 
            'Amd E-Series E2-3200': 'Amd E2-3200'
        }
    }

    opath = assign_loc(loc)
    with open(loc) as ifile, open(opath, "w", newline="") as ofile:
        reader = csv.DictReader(ifile)
        writer = csv.DictWriter(ofile, reader.fieldnames)
        writer.writeheader()
        
        # Fix some inconsinstencies and fill the missing value
        for row in reader:
            for attr, dct in to_fix.items():
                if row[attr] in dct:
                    row[attr] = dct[row[attr]]

            if row['socket'] == 'Intel Socket LGA3647' and row['brand'] == 'AMD':
                row['socket'] == 'AMD Socket F'

            # Remove prefix string from socket
            row["socket"] = row["socket"].rsplit()[-1]
            
            writer.writerow(row)
            
    os.replace(opath, loc)