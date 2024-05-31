import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from allocationModel import markowitzModel
import portfolioAllocation
from datetime import datetime
import json
import plotly.express as px

############## INPUT DATA LOADING
implemented_models = ["Markowitz", "Black-Litterman"]

### LOADING PRICE TIME SERIES
price_series = pd.read_csv("/Users/andrei/Documents/asset-allocation-data/processed/2024-05-29/all_markets_2024-05-29.csv")
price_series['DATE'] = pd.to_datetime(price_series['DATE'])
price_series.set_index('DATE', inplace=True)
market_names_full = price_series.columns.values
selected_markets_bool = [True] * len(market_names_full)

### SELECTING MARKETS
st.title("Asset Allocation Model(s)")
model_selection = st.selectbox(label="Select optimization model", options=implemented_models, index=None)

col1, col2 = st.columns(2)

with col1:
    risk_free_rate = st.number_input(label = "Risk-free rate", min_value=0.0, max_value=0.10,format="%0.3f")
with col2:
    short_selling = st.toggle(label="Short selling", value = False)
    for index, market in enumerate(market_names_full):
        selected_markets_bool[index] = st.checkbox(label=market)

unselected_markets_names = [market for market, flag in zip(market_names_full, selected_markets_bool) if not flag]
price_series = price_series.drop(unselected_markets_names, axis = 1)


### GENERATING LOG RETURNS
log_returns = portfolioAllocation.getLogReturns(price_series)
risk_free_rate = 0.03
expected_returns = portfolioAllocation.getExpectedReturns(log_returns, calendarized = True) * 252
cov_matrix = portfolioAllocation.getCovarianceMatrix(log_returns, calendarized = True) * 252

### MARKETS MAPPING JSON
with open('/Users/andrei/Documents/GitHub/asset-allocation/markets_mapping.JSON', 'r') as file:
    market_mapping = json.load(file)








    

if model_selection == implemented_models[0]:
    my_model = markowitzModel(expected_returns, cov_matrix, risk_free_rate, markets_mapping=market_mapping)
else:
    raise NotImplementedError(f"{model_selection} model has not been implemented yet!")

efficient_frontier = my_model.calculateEfficientFrontier(short_selling=short_selling)
efficient_frontier['sharpe_ratio'] = (efficient_frontier['returns'] - risk_free_rate) / efficient_frontier['volatility']
weights = efficient_frontier['weights']
returns = efficient_frontier['returns']
volatilities = efficient_frontier['volatility']
max_sharpe_return, max_sharpe_volatility = portfolioAllocation.calculate_max_sharpe_ratio(returns, volatilities, risk_free_rate)

max_sr = (max_sharpe_return - risk_free_rate) / max_sharpe_volatility


fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(volatilities, returns, c=efficient_frontier['sharpe_ratio'], marker='o')
plt.xlabel('Volatility (Standard Deviation)')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.colorbar(scatter, label='Sharpe Ratio')
plt.grid(True)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.plot([0, volatilities.max()], [risk_free_rate, volatilities.max()*max_sr+risk_free_rate], color='red', linestyle='--', linewidth=2,label='Capital Market Line (CML)')
ax.legend()
st.pyplot(fig)





weights_df = pd.DataFrame(weights.tolist())

# Plotting
fig_2, ax_2 = plt.subplots(figsize=(12, 8))

# Create stackplot
ax_2.stackplot(volatilities, weights_df.T, labels=market_names_full)

# Adding labels and title
ax_2.set_xlabel('Volatility')
ax_2.set_ylabel('Composition (%)')
ax_2.set_title('Portfolio Composition Across Efficient Frontier')


# Adding legend
ax_2.legend(title='Markets', bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)


st.pyplot(fig_2)