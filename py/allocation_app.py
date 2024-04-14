import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from portfolio_allocation import AllocationModel

data = pd.read_csv("/Users/andrei/Documents/asset-allocation-data/processed/2024-02-25/equities_2024-02-25.csv")
data['DATE'] = pd.to_datetime(data['DATE'])

allo = AllocationModel(data, 0)

expected_returns_mkw = allo.get_Portfolio_Return(allo.markowitz_portfolio())
volatility_mkw = allo.get_Portfolio_Volatility(allo.markowitz_portfolio())

st.metric(label="Expected returns", value = expected_returns_mkw, delta="Nothing here for now")
st.metric(label="Volatility", value = volatility_mkw, delta="Nothing here for now")
