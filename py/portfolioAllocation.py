### custom functions for portfolio allocation project

import pandas as pd
import numpy as np

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