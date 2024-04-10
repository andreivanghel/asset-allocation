# allocation_model.py

import numpy as np
import pandas as pd
from scipy.optimize import minimize



### TODO: 
### - output named vector / dataframe with ticker names from markowitz_portfolio() method
### - within class __init__ method, define possible ways of calculating expected returns... / treating the time series
### - create init method for passing price time series and then generating log returns -> expected_returns / cov_matrix
### - define type of input parameters in methods???



class AllocationModel:
    def __init__(self, expected_returns, cov_matrix):
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix

    def __init__(self, log_returns):
        self.expected_returns = log_returns.mean()
        self.cov_matrix = log_returns.cov()
    
    def markowitz_portfolio(self):
        def get_Portfolio_Return(weights):
            return np.sum(self.expected_returns * weights)
        
        def get_Portfolio_Volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        def get_Portfolio_Sharpe_Ratio(weights):
            return get_Portfolio_Return(weights) / get_Portfolio_Volatility(weights)
        
        n_assets = len(self.expected_returns)
        initial_weights = np.array([1 / n_assets] * n_assets)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for asset in range(n_assets))

        result = minimize(lambda x: -get_Portfolio_Sharpe_Ratio(x), 
                          initial_weights, 
                          method = 'SLSQP', 
                          bounds = bounds, 
                          constraints = constraints)

        return (result.x)

    def black_litterman_portfolio(self, views, tau=0.05):
        # Implementazione dell'algoritmo di Black-Litterman per l'allocazione del portafoglio
        pass

    # Altre funzioni per gli algoritmi di allocazione del portafoglio