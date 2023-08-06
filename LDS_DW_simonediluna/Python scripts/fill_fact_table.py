# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

Programme goals:
    * Prepare fact table:
        substitute old FKs with autogenerated PKs in dim tables
    * Upload fact table in the personal DB on SQL Server
    
Note: 
In pyodbc, connection and cursor are both context managers, therefore 
there is no need to close them when they go out of scope, see: 
	https://github.com/mkleehammer/pyodbc/wiki/Connection#close
	https://github.com/mkleehammer/pyodbc/wiki/Cursor#close
For this reason, I used them within functions. There are two benefits in this:
	1. I don't need to close them because they are automatically closed when 
        the function returns.
	2. If an error occurs while using the connection, the subsequent exit 
        from the function automatically closes the connection and the cursor. 
"""
import os
import csv
import pyodbc
from fact_table_transformations import assign_loc
from fill_dim_tables import load_data


# Function definitions
def map_code_to_id(
        tab_name: str, 
        to_map: tuple[str, str], 
        conn_str: str | dict[str, str]
    ) -> dict[int, int]:
    """
    Given a table name in the DB and a pair of attribute names, 
    return a dictionary mapping the two columns.
    """
    attr_code_name, attr_id_name = to_map
    hash_map = {}
    cur = pyodbc.connect(**conn_str).cursor()
    query = f"""
        SELECT {attr_code_name}, {attr_id_name}
        FROM {tab_name}
    """
    cur.execute(query)
    for row in cur:
        attr_code_val, attr_id_val = row
        hash_map[attr_code_val] = attr_id_val
    return hash_map

def replace_cols(
    path: str, 
    col_names_map: dict[str, str], 
    hash_tabs: dict[str, dict[int, int]]
    ) -> str:
    """ 
    Replaces the contents of N columns of the input file by means 
    of N dictionaries. Each value of a column is mapped to an exact 
    value via a dictionary. The function does not work in-palce,
    it returns the path of the new file.
    
    Parameters
    ----------
        path: The path of the file to be modified.
        
        col_names_map: A dictionary mapping the name of the column 
            to be replaced with the name of the new column.
        
        hash_tabs: A dictionary mapping the name of the column
            to be replaced with the dictionary mapping the 
            current values to the new ones.
    """
    # Create a new fact table with attr_id in place of attr_code
    new_loc = assign_loc(path)
    with (
            open(path, newline="") as ifile, 
            open(new_loc, "w", newline="") as ofile
            ):
        reader = csv.DictReader(ifile)
        new_header = []
        for var in reader.fieldnames:
            if var not in col_names_map:
                new_header.append(var)  # old attr name
            else:
                new_header.append(col_names_map[var])  #new attr name
        writer = csv.DictWriter(ofile, new_header) 
        
        # write the new fact table
        writer.writeheader()
        new_header = set(new_header)
        for row in reader:
            new_row = {}
            for col in reader.fieldnames:
                if col in new_header:
                    new_row[col] = row[col]
                else:
                    # Get mapped value from the corresponding hash table
                    new_col = col_names_map[col]
                    mapped_val = hash_tabs[col][int(row[col])]
                    new_row[new_col] = str(mapped_val)
            writer.writerow(new_row)
    return new_loc    


# Main program
if __name__ == "__main__":

    # Get the location of the fact table from the user
    loc = input("Enter the path to the .csv file of the fact table: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
    
    # Define connection string 
    user, pwd = input("Enter username and password of your server account"
                      " separated by a white space: ").split()
    conn_string = dict(
        driver="{ODBC Driver 18 for SQL Server}",                  
        host="tcp:131.114.72.230", 
        database="simonediluna_DB", 
        user=user, 
        password=pwd, 
        encrypt="no"
    )
    
    # Define parameters
    tables = {
        "cpu_product": ("cpu_code", "cpu_id"), 
        "geography": ("geo_code", "geo_id"), 
        "vendor": ("vendor_code", "vendor_id")
    }
    map_code_id_names = dict(tables.values())
    
    # Map codes to ids
    hash_tabs = {}
    for tab_name, attr_pair in tables.items():
        hash_tab = map_code_to_id(tab_name, attr_pair, conn_string)
        hash_tabs[attr_pair[0]] = hash_tab
       
    # Create a new fact table with attr_ids in place of attr_codes
    new_loc = replace_cols(loc, map_code_id_names,hash_tabs)

    ## Map the local name of the fact table to its name in the database
    fact_tab_name = os.path.basename(new_loc).removesuffix(".csv")
    fact_tab_name_map = {fact_tab_name: "cpu_sales_fact"}
    
    # Upload the content of the fact table in the DB    
    load_data([new_loc], fact_tab_name_map, conn_string)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    