import pandas as pd
import numpy as np

def missingValuesTest(pricesTimeSeriesDf: pd.DataFrame, maxAcceptableMissingRows: float = 0.2):    

    na_rows = len(pricesTimeSeriesDf) - len(pricesTimeSeriesDf.dropna())
    test_metric = na_rows / (len(pricesTimeSeriesDf))

    if test_metric > maxAcceptableMissingRows:
        print(f"Warning! Number of rows with missing values ({na_rows}) is higher than {maxAcceptableMissingRows * 100}% of total rows ({len(pricesTimeSeriesDf)})")
        print(f"Percentage of missing rows: {round(test_metric * 100, 2)}%")
        test_outcome = False
        test_outcome_text = f"{test_metric} > {maxAcceptableMissingRows}"
    else:
        test_outcome = True
        test_outcome_text = f"{test_metric} < {maxAcceptableMissingRows}"

    output = {"Test name": "Missing values test",
              "Test metric": test_metric,
              "Test threshold": maxAcceptableMissingRows,
              "Test outcome": test_outcome,
              "Test": test_outcome_text}
    
    return output

def timeSeriesLengthTest(pricesTimeSeriesDf: pd.DataFrame, minAcceptableLength: float = 252 * 3):
    
    pricesTimeSeriesDf_clean  = pricesTimeSeriesDf.dropna()
    test_metric = len(pricesTimeSeriesDf_clean)

    if test_metric < minAcceptableLength:
        print(f"Warning!The total number of rows ({test_metric}) is lower than the minimum acceptable length ({minAcceptableLength})")
        test_outcome = False
        test_outcome_text = f"{test_metric} < {minAcceptableLength}"
    else:
        test_outcome = True
        test_outcome_text = f"{test_metric} > {minAcceptableLength}"
    
    output = {"Test name": "Time series length",
              "Test metric": test_metric,
              "Test threshold": minAcceptableLength,
              "Test outcome": test_outcome,
              "Test": test_outcome_text}
    
    return output

