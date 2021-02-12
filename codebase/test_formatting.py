# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 13:34:08 2021

original file: https://github.com/reichlab/covid19-forecast-hub-validations/blob/main/code/test_formatting.py

@author: Jannik Deuschel
"""

from .covid19 import validate_quantile_csv_file
import pandas as pd


def validate_forecast_file(filepath, silent=False):
    """
    purpose: Validates the forecast file with zoltpy 
    link: https://github.com/reichlab/zoltpy/blob/master/zoltpy/covid19.py
    params:
    * filepath: Full filepath of the forecast
    """
    file_error = validate_quantile_csv_file(filepath, silent=silent)
    
    
    if file_error != "no errors":
        return True, file_error
    else:
        return False, file_error


def forecast_check(filepath):
    is_error, forecast_error_output = validate_forecast_file(filepath)
    
    # valdate predictions
    #if not is_error:
    #    is_error, forecast_error_output = validate_forecast_values(filepath)
    

    # Add to previously checked files
    output_error_text = compile_output_errors(filepath,
                                              False, [],
                                              is_error, forecast_error_output)
    return output_error_text
        

def compile_output_errors(filepath, is_filename_error, filename_error_output, is_error, forecast_error_output):
    """
    purpose: update locally_validated_files.csv and remove deleted files
    params:
    * filepath: Full filepath of the forecast
    * is_filename_error: Filename != file path (True/False)
    * filename_error_output: Text output error filename != file path
    * is_error: Forecast file has error (True/False)
    * forecast_error_output: Text output forecast file error
    * is_date_error: forecast_date error (True/False)
    * forecast_date_output: Text output forecast_date error
    """
    # Initialize output errors as list
    output_error_text = []

    # Iterate through params
    error_bool = [is_filename_error, is_error]
    error_text = [filename_error_output, forecast_error_output]

    # Loop through all possible errors and add to final output
    for i in range(len(error_bool)): 
        if error_bool[i]:  # Error == True
            output_error_text += error_text[i]

    # Output errors if present as dict
    # Output_error_text = list(chain.from_iterable(output_error_text))
    return output_error_text

def print_output_errors(output_errors, prefix=""):
    """
    purpose: Print the final errors
    params:
    * output_errors: Dict with filepath as key and list of errors error as value
    """
    # Output list of Errors
    if len(output_errors) > 0:
        for filename, errors in output_errors.items():
            print("\n* ERROR IN ", filename)
            for error in errors:
                print(error)
        print("\n✗ %s error found in %d file%s. Error details are above." % (prefix, len(output_errors) ,("s" if len(output_errors)>1 else "")))
    else:
        print("\n✓ no %s errors"% (prefix))