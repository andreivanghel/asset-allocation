### custom functions for portfolio allocation project

import pandas as pd
import numpy as np
import great_expectations as ge

def validate(pricesTimeSeriesDf: pd.DataFrame, missingValuesThreshold: float = 0.2):
    ### TEST 1 - MISSING VALUES (place functions in external module)
    na_rows = pricesTimeSeriesDf.isnull().sum()
    test_metric = na_rows / (len(pricesTimeSeriesDf))
    if test_metric > missingValuesThreshold:
        print(f"Warning! Number of rows with missing values ({na_rows}) is higher than {missingValuesThreshold * 100}% of total rows ({len(pricesTimeSeriesDf)})")
        print(f"Percentage of missing rows: {test_metric * 100}%")
    
    pass

def getLogReturns(pricesTimeSeriesDf: pd.DataFrame):
    logRet = pricesTimeSeriesDf.apply(lambda x: np.log(x) - np.log(x.shift(1)))
    return logRet

def calendarizedReturns(logReturnsDf: pd.DataFrame):
    days_distance = logReturnsDf.index.to_series().diff().dt.days
    adjusted_returns = logReturnsDf.div(days_distance, axis = 0)
    return adjusted_returns

def getExpectedReturns(logReturnsDf: pd.DataFrame, calendarized: bool = False):
    if calendarized: logReturnsDf = calendarizedReturns(logReturnsDf)
    expected_returns = logReturnsDf.mean()
    return expected_returns

def getCorrelationMatrix(logReturnsDf: pd.DataFrame, calendarized: bool = False):
    if calendarized: logReturnsDf = calendarizedReturns(logReturnsDf)
    cmat = logReturnsDf.corr()
    return cmat

