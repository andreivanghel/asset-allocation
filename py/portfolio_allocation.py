# allocation_model.py

import numpy as np
import pandas as pd
from scipy.optimize import minimize



### TODO: 
### - output named vector / dataframe with ticker names from markowitz_portfolio() method
### - within class' __init__ method, define possible ways of calculating expected returns... / treating the time series
### - create init method for passing price time series and then generating log returns -> expected_returns / cov_matrix
### - define type of input parameters in methods???



class AllocationModel:
    def __init__(self, price_time_series: pd.DataFrame, frequency):
        self.tickers = price_time_series.drop("DATE", axis = 1).columns
        log_returns = price_time_series.set_index("DATE")[self.tickers].apply(lambda x: np.log(x) - np.log(x.shift(1)))

        ### data quality check
        null_ratio = log_returns.isnull().sum() / log_returns.shape[0]
        available_obs = log_returns.shape[0] - log_returns.isnull().sum()

        print("Null ratio: \n", null_ratio)
        print("Available observations: \n", available_obs)

        null_threshold = 0.2
        leng_threshold = 252 * 5

        rel_NA_check = null_ratio[null_ratio > null_threshold]
        abs_NA_check = available_obs[available_obs < leng_threshold]

        if(len(rel_NA_check) > 0):
            print("The following indexes have a ratio of NAs greater than", null_threshold, ": \n", rel_NA_check)
        if(len(abs_NA_check) > 0):
            print("The following indexes have a number of observation lower than", leng_threshold, ": \n", abs_NA_check)

        ### calculate annual expected returns and variance / covariance matrix
        self.expected_returns = log_returns.mean() * 252
        self.cov_matrix = log_returns.cov() * 252



    
    def get_tickers(self):
        return(self.tickers)

    def get_expected_returns(self):
        return(self.expected_returns)
    
    def get_cov_matrix(self):
        return(self.cov_matrix)
    

    def get_Portfolio_Return(self, weights):
        return np.sum(self.expected_returns * weights)
        
    def get_Portfolio_Volatility(self, weights):
        return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
    def get_Portfolio_Sharpe_Ratio(self, weights):
        return self.get_Portfolio_Return(weights) / self.get_Portfolio_Volatility(weights)
    
    def markowitz_portfolio(self):
        
        
        n_assets = len(self.expected_returns)
        initial_weights = np.array([1 / n_assets] * n_assets)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for asset in range(n_assets))

        result = minimize(lambda x: -self.get_Portfolio_Sharpe_Ratio(x), 
                          initial_weights, 
                          method = 'SLSQP', 
                          bounds = bounds, 
                          constraints = constraints)
        
        portfolio_weights = pd.Series(result.x, index=self.expected_returns.index)
        return portfolio_weights

    def black_litterman_portfolio(self, views, tau=0.05):
        # Implementazione dell'algoritmo di Black-Litterman per l'allocazione del portafoglio
        pass

    # Altre funzioni per gli algoritmi di allocazione del portafoglio