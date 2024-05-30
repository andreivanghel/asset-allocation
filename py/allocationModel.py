from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import portfolioAllocation as pfAl
import math
from scipy.optimize import minimize
from typing import Tuple

class aaModel(ABC):

    @abstractmethod
    def calculateEfficientFrontier(self):
        raise NotImplementedError("This method should be implemented by the subclass!")

class markowitzModel(aaModel):

    def __init__(self, expected_returns: pd.Series, cov_matrix: pd.DataFrame, risk_free_rate: float, markets_mapping: dict) -> None:
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.risk_free_rate = risk_free_rate


        markets_mapping_filt = {key: value for key, value in markets_mapping.items() if value}
        markets = []
        asset_classes = []

        for asset_class, items in markets_mapping_filt.items():
            for item in items:
                markets.append(item['market'])
                asset_classes.append(asset_class)
        
        markets_asset_classes = pd.DataFrame({'market': markets, 'asset_class': asset_classes})
        markets_asset_classes = markets_asset_classes[markets_asset_classes["market"].isin(expected_returns.index)]
        
        self.markets_mapping = markets_mapping_filt
        self.markets_asset_classes = markets_asset_classes
    
    def formatConstraints(self, allocation_constraints: pd.DataFrame, bounds: list) -> Tuple[tuple, list]:
        constraints = []

        for _, row in allocation_constraints.iterrows():
            market = row["market"]
            sign = row["sign"]
            pctg = float(row["percentage"])
            cs_type = row["constraint_type"]

            mkt_weight_idx = self.expected_returns.index.get_loc(market)
            print(mkt_weight_idx)
            if cs_type == "absolute":
                
                if sign == "<":
                    bounds[mkt_weight_idx][1] = pctg
                elif sign == ">":
                    bounds[mkt_weight_idx][0] = pctg
                elif sign == "=":
                    constraints.append({'type': 'eq', 'fun': lambda x, idx=mkt_weight_idx, p=pctg: x[idx] - p})
                else:
                    raise ValueError(f"Invalid sign '{sign}' in allocation constraints. Valid signs are '<', '>', '='.")
                
            elif cs_type == "relative":
                asset_class = self.markets_asset_classes.loc[self.markets_asset_classes['market'] == market, 'asset_class'].values[0]
                asset_class_idxs = self.expected_returns.index.get_indexer(self.markets_asset_classes.loc[self.markets_asset_classes['asset_class'] == asset_class, 'market'])
                
                if sign == "<":
                    constraints.append({'type': 'ineq', 'fun': lambda x, idxs=asset_class_idxs, idx=mkt_weight_idx, p=pctg: p * np.sum(x[idxs]) - x[idx]})
                elif sign == ">":
                    constraints.append({'type': 'ineq', 'fun': lambda x, idxs=asset_class_idxs, idx=mkt_weight_idx, p=pctg: x[idx] - p * np.sum(x[idxs])})
                elif sign == "=":
                    constraints.append({'type': 'eq', 'fun': lambda x, idxs=asset_class_idxs, idx=mkt_weight_idx, p=pctg: (x[idx] / np.sum(x[idxs])) - p})
                else:
                    raise ValueError(f"Invalid sign '{sign}' in allocation constraints. Valid signs are '<', '>', '='.")
            
            else:
                raise ValueError(f"Invalid constraint type '{cs_type}' in allocation constraints. Valid signs are 'absolute', 'relative'.")

        bounds = tuple(map(tuple, bounds))
        return bounds, constraints
                
                


    def calculateEfficientFrontier(self, short_selling: bool = False, volatilities: pd.Series = None, allocation_constraints: pd.DataFrame = None):
        num_assets = len(self.expected_returns)
        results = {'returns': [], 'volatility': [], 'weights': []}

        bounds = list([0, 1] if not short_selling else [-math.inf, math.inf] for _ in range(num_assets))
        print(bounds)
        w_constraints = []

        if allocation_constraints is not None:
            bounds, w_constraints = self.formatConstraints(allocation_constraints, bounds)
        w_constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        print("bounds",bounds)
        min_vol_result = minimize(lambda weights: pfAl.portfolio_volatility(weights, self.cov_matrix), num_assets * [1. / num_assets], method='SLSQP', bounds=bounds, constraints=w_constraints)
        max_ret_result = minimize(lambda weights: -pfAl.portfolio_returns(weights, self.expected_returns), num_assets * [1. / num_assets], method='SLSQP', bounds=bounds, constraints=w_constraints)

        min_return = pfAl.portfolio_returns(min_vol_result.x, self.expected_returns)
        max_return = pfAl.portfolio_returns(max_ret_result.x, self.expected_returns)


        returns = np.linspace(min_return, max_return, 100)

        for target_return in returns:

            constraints = (
                *w_constraints,
                {'type': 'eq', 'fun': lambda x, target=target_return: pfAl.portfolio_returns(x, self.expected_returns) - target}
            )

            result = minimize(lambda weights: pfAl.portfolio_volatility(weights, self.cov_matrix), num_assets*[1./num_assets,], method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                returns = pfAl.portfolio_returns(result.x, self.expected_returns)
                volatility = pfAl.portfolio_volatility(result.x, self.cov_matrix)

                results['returns'].append(returns)
                results['volatility'].append(volatility)
                results['weights'].append(result.x)
            else:
                print(f"Optimization failed for target {target_return}")

        efficient_frontier = pd.DataFrame(results)
        return efficient_frontier
