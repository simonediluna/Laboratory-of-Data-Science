# -*- coding: utf-8 -*-
"""
@author: Simone Di Luna
@python: 3.11.4
@OS: Windows 11

Programme goals:
    * Check semantic accuracy of attributes.
    * Rename all attributes
    * Add attributes: the_quarter, day_name.
"""

import csv
import os
from fact_table_transformations import rename_attrs, modify_table


# Function definitions
def is_leap_year(year: int) -> bool:
    """
    Check if the input year is a leap year. It is only used to
    define the test of the find_day_name function. 
    """
    if year % 4 == 0:
        # Secular years not divisible by 400 are not leap years
        if year % 100 == 0:
            return True if year % 400 == 0 else False
        return True
    return False

def find_day_name(fact_time_id: str):
    """
    Given the date of a fact, find the day on which it occurred. 
    The time reference point used is Thursday 1 January 1970, the Unix epoch.
    Therefore this function works correctly only with input dates >= the 
    Unix epoch. This function was designed to be used as an argument in 
    the modify_table function.
    
    fact_time_id: The time_id associated to the fact.
    """
    # Define map tables
    days_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                  'Friday', 'Saturday']
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Unix epoch variables
    ref_year = 1970
    ref_day_of_week = 4  # Thursday. Range 0 to 6.
    
    fact_year, fact_month, fact_day = (
        int(fact_time_id[:4]), 
        int(fact_time_id[4:6]), 
        int(fact_time_id[6:])
    )
    
    # Number of leap years elapsed. The current year is counted.
    # Starting from 1970, the first leap year is 1972.
    n_leap_years = 0
    year = 0  # Assign a value to year in case the loop doesn't start
    for year in range(ref_year + 2, fact_year + 1, 4):
        if year % 100 or year % 400 == 0:
            n_leap_years += 1 
            
    # If current year is leap and the fact date is before 29 Feb
    # then remove the previously added leap year.
    if year == fact_year and (year % 100 or year % 400 == 0):
        if fact_month < 3:
            n_leap_years -= 1
    
    # Find the number of days elapsed since the beginning of the year
    n_days_elapsed_curr_year = sum(days_in_month[:fact_month-1]) + fact_day
    
    # Since 365 % 7 == 1, the 1 Jan of each new year, the day of week 
    # is increased by 1 with rispect to the 1 Jan of the prev year 
    # (not considering leap years).
    fact_day_of_week = (ref_day_of_week + fact_year - ref_year + 
                        n_days_elapsed_curr_year + n_leap_years - 1) % 7
    
    return days_name[fact_day_of_week]

def compute_quarter(month: str):
    """
    Determine the quarter starting from the month of the year. This function 
    was designed to be used as an argument in the modify_table function.
    """
    return ["Q1", "Q2", "Q3", "Q4"][(int(month)-1) // 3]    

def check_time_dim(path: str, time_id_name: str = "time_code", 
                   attr_names: tuple[str, str, str] = ('year','month','day')):
    """
    Assert semantic accuracy of the time dimension.
    
    Parameter
    ---------
        time_id_name: Attribute name of the column storing the time id 
            formated as YYYYMMDD.
            
        attr_names: The 3-tuple containing the column names referring to year, 
            month and day respectively.
        
    """
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            year, month, day = [int(row[t]) for t in attr_names]
            computed_time_id = year*10_000 + month*100 + day
            assert int(row[time_id_name]) == computed_time_id


################### Test the find_day_name function #################
# import datetime
# import random

# day_map = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
#               'Friday', 'Saturday', 'Sunday', ]
# days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# months = list(range(1, 13))
# years = list(range(1970, 3000))
# dct = dict(zip(months, days_in_month))

# for _ in range(10_000):
#     year = random.choice(years)
#     month = random.choice(months)
#     if is_leap_year(year):
#         dct[2] += 1
#         day = random.randint(1, dct[month])
#         dct[2] -= 1
#     else:
#         day = random.randint(1, dct[month])

#     date = year, month, day
#     str_date = str(year)
#     for n in (month, day):
#         if n < 10:
#             str_date += '0' + str(n)
#         else:
#             str_date += str(n)
#     day_num = datetime.date(*date).weekday() # Monday == 0
#     true = day_map[day_num]
#     predict = find_day_name(str_date)
    
#     assert true == predict, (date, true, predict)              
        

# Main program
if __name__ == "__main__":
    
    # Get the location of the file from the user
    loc = input("Enter the path to the .csv file: ")
    while not os.path.exists(loc):
        loc = input("The path does not exist, please enter a valid path: ")
        
    # Assert the semantic of the attributes in the time dimension
    check_time_dim(loc)

    # Define function arguments
    to_rename ={
        "time_code": "time_id",
        "year": "the_year",
        "month": "month_of_year",
        "day": "day_of_month",
        "week": "week_of_year"
        }
    to_add = {
        "the_quarter": {"func":  compute_quarter, "attr": "month_of_year"},
        "day_name": {"func":  find_day_name, "attr": "time_id"}
        }
    
    # Run functions
    loc = rename_attrs(loc, to_rename)
    modify_table(loc, to_add=to_add, inplace=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    