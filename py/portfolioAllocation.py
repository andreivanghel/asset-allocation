### custom functions for portfolio allocation project

import pandas as pd
import numpy as np
import great_expectations as ge
import inputValidation
from prettytable import PrettyTable

def validate(pricesTimeSeriesDf: pd.DataFrame):
    ### TEST 1 - MISSING VALUES
    test_1_output = inputValidation.missingValuesTest(pricesTimeSeriesDf)

    ### TEST 2 - TIME SERIES LENGTH
    test_2_output = inputValidation.timeSeriesLengthTest(pricesTimeSeriesDf)

    ### PRESENTING THE RESULTS
    table = PrettyTable()
    table.field_names = ["Test name", "Passed", "Test values"]

    table.add_row([test_1_output["Test name"], test_1_output["Test outcome"], test_1_output["Test"]])
    table.add_row([test_2_output["Test name"], test_2_output["Test outcome"], test_2_output["Test"]])

    print(table)
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

