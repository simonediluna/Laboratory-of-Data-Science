# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

Programme goals:
    * Rename attribute: name.
"""

import os
from fact_table_transformations import rename_attrs


if __name__ == "__main__":
    
    # Get the location of the file from the user
    loc = input("Enter the path to the .csv file: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
        
    # Rename attribute "name" in "cpu_name"
    to_rename = {"name": "vendor_name"}
    rename_attrs(loc, to_rename)
