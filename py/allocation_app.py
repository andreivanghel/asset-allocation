import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from allocationModel import markowitzModel
import portfolioAllocation
import json

############## INPUT DATA LOADING
implemented_models = ["Markowitz", "Black-Litterman"]

### LOADING FX TIME SERIES
fx_series = pd.read_csv("FX_2024-06-02.csv")
fx_series['DATE'] = pd.to_datetime(fx_series['DATE'])
fx_series.set_index('DATE', inplace=True)

### LOADING PRICE TIME SERIES
price_series_untreated = pd.read_csv("all_markets_2024-06-02.csv")
price_series_untreated['DATE'] = pd.to_datetime(price_series_untreated['DATE'])
price_series_untreated.set_index('DATE', inplace=True)

### MARKETS MAPPING JSON
with open('markets_mapping.JSON', 'r') as file:
    market_mapping = json.load(file)



### SELECTING MARKETS
st.title("Asset Allocation Model(s)")
st.markdown("Author: Andrei Vanghel")
st.write("")
model_selection = st.selectbox(label="Select optimization model", options=implemented_models, index=None)


with st.container(border=True):
    with st.expander("Model settings"):
        mkts_column, other_settings = st.columns([3,2])
        with other_settings:
            initial_sampling_date = st.date_input("Select the initial sampling date", min_value=price_series_untreated.index.min(), value=pd.to_datetime("2007-01-01"), max_value=price_series_untreated.index.max())
            final_sampling_date = st.date_input("Select the final sampling date", min_value=price_series_untreated.index.min(), max_value=price_series_untreated.index.max())
            initial_sampling_date = pd.to_datetime(initial_sampling_date)
            final_sampling_date = pd.to_datetime(final_sampling_date)
            price_series_untreated = price_series_untreated.loc[(price_series_untreated.index >= initial_sampling_date) & (price_series_untreated.index <= final_sampling_date)] 
            price_series = portfolioAllocation.forexPriceTransformation(pricesTimeSeriesDf=price_series_untreated,
                                                                        forexTimeSeriesDf=fx_series,
                                                                        markets_mapping=market_mapping,
                                                                        analysisCurrency="USD") # analysis currency to be parametrized
            risk_free_rate = st.number_input(label = "Risk-free rate", min_value=0.0, max_value=0.10,format="%0.3f")
            short_selling = st.toggle(label="Short selling", value = False)
            calendarized = st.toggle(label="'Calendarized' log-returns", value = True)

        with mkts_column:
            market_names_full = price_series.columns.values
            selected_markets_bool = [True] * len(market_names_full)
            for index, market in enumerate(market_names_full):
                selected_markets_bool[index] = st.checkbox(label=market, value = True)

    
    plot_right_lim = np.sqrt(np.diag(portfolioAllocation.getCovarianceMatrix(portfolioAllocation.getLogReturns(price_series), calendarized=calendarized)*252)).max()


    unselected_markets_names = [market for market, flag in zip(market_names_full, selected_markets_bool) if not flag]
    price_series = price_series.drop(unselected_markets_names, axis = 1)
    selected_markets = price_series.columns

    ### GENERATING LOG RETURNS
    log_returns = portfolioAllocation.getLogReturns(price_series)
    expected_returns = portfolioAllocation.getExpectedReturns(log_returns, calendarized = calendarized) * 252
    cov_matrix = portfolioAllocation.getCovarianceMatrix(log_returns, calendarized = calendarized) * 252
    st_devs = np.sqrt(np.diag(cov_matrix))
    correlation_matrix = cov_matrix / np.outer(st_devs, st_devs)

    expected_returns_pct = ["{:.2f}%".format(val * 100) for val in expected_returns]
    st_devs_pct = ["{:.2f}%".format(val * 100) for val in st_devs]
    results_df = pd.DataFrame({
        "Expected Returns": expected_returns_pct,
        "Standard Deviation": st_devs_pct
    }, index=expected_returns.index)


    with st.expander("Markets statistics"):
        st.table(results_df)

        cmat, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        ax.set_title('Correlation Matrix')
        st.pyplot(cmat)




############## EFFICIENT FRONTIER

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
plt.xlim(left=0, right = plot_right_lim*1.05)
plt.ylim(bottom=0)
plt.plot([0, volatilities.max()], [risk_free_rate, volatilities.max()*max_sr+risk_free_rate], color='red', linestyle='--', linewidth=2,label='Capital Market Line (CML)')
ax.legend()
st.pyplot(fig)





weights_df = pd.DataFrame(weights.tolist())

# Plotting
fig_2, ax_2 = plt.subplots(figsize=(12, 8))
ax_2.stackplot(volatilities, weights_df.T, labels=selected_markets)
ax_2.set_xlabel('Volatility')
ax_2.set_ylabel('Composition (%)')
ax_2.set_title('Portfolio Composition Across Efficient Frontier')
ax_2.legend(title='Markets', bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3)


st.pyplot(fig_2)



st.write("\n\n\n\n\n")
st.markdown("[by Andrei Vanghel](https://github.com/andreivanghel)")