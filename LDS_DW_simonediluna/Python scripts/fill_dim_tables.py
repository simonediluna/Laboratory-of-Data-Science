# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

Programme goals:
    * Upload dimension tables:
        Load the transformed data into the personal database in SQL Server. 
        
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

# Function definitions
def load_data( 
    files: list[str],
    map_tab_names: dict[str, str],
    conn_str: str | dict[str, str],
    batch_size = 2000
    ):
    """
    Loads the data into the database on the server via the database 
    cursor passed in input.
    
    Parameters
    ----------
        files: The path of the folder containing the location to the .csv
            files to upload in the server.
            
        map_tab_names: A dictionary mapping the local file names to the
            actial name of the tables in the database.
        
        conn_str: the connection string to pass as argument in pyodbc.connect
            function to connect to the DB. It can be a string or a dictionary
            containing keyword: value pairs.
        
        batch_size: Number of records to be execute before committing.
    """
    # Connect to the db
    if isinstance(conn_str, str):
        cur = pyodbc.connect(conn_str).cursor()
    else:
        cur = pyodbc.connect(**conn_str).cursor()
        
    print(f"{'Start of the loading process':*^50}")  
    for tab_path in files:
        with open(tab_path, newline="") as file:
            
            # Retrieve parameters to pass to the SQL query
            reader = csv.reader(file)
            header = next(reader)
            attributes = ",".join(header)
            params = ",".join(["?"] * len(header))
            file_tab_name = os.path.basename(tab_path).removesuffix(".csv")
            db_tab_name = map_tab_names[file_tab_name]
            
            
            query = f"""
                INSERT INTO {db_tab_name} ({attributes})
                VALUES ({params})
            """
            
            # Upload data
            cnt = 0  # Number of records processed
            n_commits = 0
            for row in reader:
                cur.execute(query, row)
                cnt += 1
                
                if cnt == batch_size:
                    cur.commit()
                    n_commits += 1
                    cnt = 0
                    print(f"\r\tNumber of batches commited: {n_commits}", 
                          end="\r")  # \r at the beginning is required due to a console bug
            cur.commit()  # Commit the remaining executed records < batch_size
        
        print("\n" + file_tab_name + ".csv", "file processed successfully")
    print(f"{'End of the loading process':*^50}")



if __name__ == "__main__":
    
    # Get the location of the dimension tables from the user
    loc = input("Enter the path to the .csv file(s) of the "
                "dimension tables to be uploaded to the server: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
    if os.path.isfile(loc):
        files = [loc]
    else:
        files = [loc + "\\" + file_name for file_name in os.listdir(loc) 
                 if file_name.endswith(".csv")]
    
    # Define function arguments
    local_dim_tab_names = "cpu geography time vendor".split()
    db_dim_tab_names = "cpu_product geography time_by_day vendor".split()
    map_tab_names = dict(zip(local_dim_tab_names, db_dim_tab_names))
        
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

    # Upload data in the DB
    load_data(files, map_tab_names, conn_string)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    