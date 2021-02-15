# -*- coding: utf-8 -*-
"""

oroginal file: https://github.com/reichlab/covid19-forecast-hub-validations/blob/main/code/validation_functions/forecast_filename.py

Created on Fri Feb 12 16:05:22 2021

@author: Jannik
"""

import pandas as pd
import os
from datetime import datetime
import pytz

def filename_match_forecast_date(filepath):
    df = pd.read_csv(filepath)
    file_forecast_date = os.path.basename(os.path.basename(filepath))[:10]
    forecast_date_column = set(list(df['forecast_date']))
    if len(forecast_date_column) > 1:
        return True, "FORECAST DATE ERROR: %s has multiple forecast dates: %s. Forecast date must be unique" % (
            filepath, forecast_date_column)
    else:
        forecast_date_column = forecast_date_column.pop()
        if (file_forecast_date != forecast_date_column):
            return True, "FORECAST DATE ERROR %s forecast filename date %s does match forecast_date column %s" % (
                filepath, file_forecast_date, forecast_date_column)
        today = datetime.now(pytz.timezone('Europe/Berlin')).date()
        forecast_date = datetime.strptime(file_forecast_date, "%Y-%m-%d").date()
        if abs(forecast_date.day - today.day) >1 or forecast_date.month != today.month or forecast_date.year != today.year:
            warning = f"Warning: The forecast is not made today. date of the forecast - {file_forecast_date}, today -  {today}."
            print(f"::warning file={os.path.basename(os.path.basename(filepath))}::{warning}")
            return True, warning
        else:
            return False, "no errors"