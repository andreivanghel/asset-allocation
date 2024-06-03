### custom functions for portfolio allocation project

import pandas as pd
import numpy as np
#import great_expectations as ge
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

def forexPriceTransformation(pricesTimeSeriesDf: pd.DataFrame, forexTimeSeriesDf: pd.DataFrame, markets_mapping: dict, analysisCurrency: str = "USD"):
    price = pricesTimeSeriesDf.copy()
    markets_in_df = price.columns

    markets_mapping_filt = {key: value for key, value in markets_mapping.items() if value}
    markets = []
    currencies = []

    for category in markets_mapping_filt.values():
        for item in category:
            markets.append(item['market'])
            currencies.append(item['currency'])
    
    markets_currency = pd.DataFrame({'market': markets, 'currency': currencies})
    markets_currency = markets_currency[markets_currency["market"].isin(markets_in_df)]

    for market in markets_in_df:
        currency = str(markets_currency.loc[markets_currency["market"] == market, "currency"].values[0])

        if currency != analysisCurrency:
            fx_column = analysisCurrency + "_" + currency
            fx_first_date = forexTimeSeriesDf[fx_column].dropna().index.min()

            price.loc[price.index < fx_first_date, market] = np.nan # NaN for observations without FX related obs.
            obs_dates = price[market].dropna().index

            price.loc[obs_dates, market] = price.loc[obs_dates, market] * forexTimeSeriesDf.loc[obs_dates, fx_column]

    return price


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

def getCovarianceMatrix(logReturnsDf: pd.DataFrame, calendarized: bool = False):
    if calendarized: logReturnsDf = calendarizedReturns(logReturnsDf)
    covmat = logReturnsDf.cov()
    return covmat

def portfolio_returns(weights, expected_returns):
    returns = np.dot(weights, expected_returns)
    return returns

def portfolio_volatility(weights, covariance_matrix):
    volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
    return volatility

def calculate_max_sharpe_ratio(returns, volatilities, risk_free_rate):
    sharpe_ratios = (returns - risk_free_rate) / volatilities
    max_sharpe_idx = np.argmax(sharpe_ratios)
    return returns[max_sharpe_idx], volatilities[max_sharpe_idx]

def marketCapTransformation(market_capitalization: dict, forexTimeSeriesDf: pd.DataFrame, markets_mapping: dict, analysisCurrency: str = "USD") -> pd.DataFrame:
    market_capitalization = {key: value for key, value in market_capitalization.items() if value}

    fx_source_date = pd.to_datetime(market_capitalization['FX_SOURCE_DATE'])

    market_capitalization.pop('FX_SOURCE_DATE', None)

    markets = []
    mkt_capp = []

    for category in market_capitalization.values():
            for item in category:
                conversion = 1
                if item['unit'] == "mln": conversion = 1000000
                if item['unit'] == "bln": conversion = 1000000000
                markets.append(item['market'])
                mkt_capp.append(float(item['market_cap']) * conversion)

    market_capitalization_df = pd.DataFrame([mkt_capp], columns=markets, index=[fx_source_date])
    market_capitalization_new = market_capitalization_df.copy()

    fx_converted_mkt_cap = forexPriceTransformation(pricesTimeSeriesDf=market_capitalization_new,
                                                    forexTimeSeriesDf=forexTimeSeriesDf,
                                                    markets_mapping=markets_mapping,
                                                    analysisCurrency=analysisCurrency)
    return(fx_converted_mkt_cap)