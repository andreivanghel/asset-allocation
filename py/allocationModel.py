from abc import ABC, abstractmethod
import pandas as pd

class aaModel(ABC):

    @abstractmethod
    def calculateEfficientFrontier(self):
        pass

class markowitzModel(aaModel):

    def __init__(self, expected_returns: pd.Series, correlation_matrix: pd.DataFrame, risk_free_rate: float, short_selling: bool = False) -> None:
        self.expected_returns = expected_returns
        self.correlation_matrix = correlation_matrix
        self.risk_free_rate = risk_free_rate
    
    def calculateEfficientFrontier(self):
        return super().calculateEfficientFrontier()