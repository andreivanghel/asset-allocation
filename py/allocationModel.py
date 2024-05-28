from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import portfolioAllocation as pfAl
import math
from scipy.optimize import minimize

class aaModel(ABC):

    @abstractmethod
    def calculateEfficientFrontier(self):
        raise NotImplementedError("This method should be implemented by the subclass!")

class markowitzModel(aaModel):

    def __init__(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame, risk_free_rate: float) -> None:
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.risk_free_rate = risk_free_rate
    
    def calculateEfficientFrontier(self, short_selling: bool = False, volatilities: pd.Series = None):
        std_devs = np.sqrt(np.diag(self.cov_matrix))
        num_assets = len(self.expected_returns)
        results = {'returns': [], 'volatility': [], 'weights': []}

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) if not short_selling else (-math.inf, math.inf) for _ in range(num_assets))

        min_vol_result = minimize(lambda weights: pfAl.portfolio_volatility(weights, self.cov_matrix), num_assets * [1. / num_assets], method='SLSQP', bounds=bounds, constraints=constraints)
        min_volatility = pfAl.portfolio_volatility(min_vol_result.x, self.cov_matrix)
        max_volatility = np.sqrt(self.cov_matrix.loc[self.expected_returns.idxmax(), self.expected_returns.idxmax()])

        if volatilities is None:
            volatilities = np.linspace(min_volatility, max_volatility, 100)

        for target_volatility in volatilities:

            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: pfAl.portfolio_volatility(x, self.cov_matrix) - target_volatility}
            )

            result = minimize(lambda weights: -pfAl.portfolio_returns(weights, self.expected_returns), num_assets*[1./num_assets,], method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                returns = pfAl.portfolio_returns(result.x, self.expected_returns)
                volatility = pfAl.portfolio_volatility(result.x, self.cov_matrix)

                results['returns'].append(returns)
                results['volatility'].append(volatility)
                results['weights'].append(result.x)

        efficient_frontier = pd.DataFrame(results)
        return efficient_frontier
