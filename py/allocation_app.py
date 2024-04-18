import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from portfolio_allocation import AllocationModel
import utils
from datetime import datetime
import json
import plotly.express as px

data = pd.read_csv("/Users/andrei/Documents/asset-allocation-data/processed/2024-02-25/equities_2024-02-25.csv")
data['DATE'] = pd.to_datetime(data['DATE'])

with open("/Users/andrei/Documents/GitHub/asset-allocation/market_capitalization.JSON", 'r') as mkt_cap_json:
    mkt_cap = json.load(mkt_cap_json)


allo = AllocationModel(data, mkt_cap)

expected_returns_mkw = allo.get_Portfolio_Return(allo.markowitz_portfolio())
volatility_mkw = allo.get_Portfolio_Volatility(allo.markowitz_portfolio())

expected_returns_mkt_neut = allo.get_Portfolio_Return(allo.market_neutral_portfolio())
volatility_mkt_neut = allo.get_Portfolio_Volatility(allo.market_neutral_portfolio())

st.markdown("# Asset allocation")

left_column_1, right_column_1 = st.columns(2)

left_column_1.write("Market neutral portfolio")
left_column_1.metric(label="Expected returns", value = round(expected_returns_mkt_neut * 100, 2), delta="Nothing here for now")
left_column_1.metric(label="Volatility", value = round(volatility_mkt_neut * 100, 2), delta="Nothing here for now")

right_column_1.write("Markowitz portfolio")
right_column_1.metric(label="Expected returns", value = round(expected_returns_mkw * 100, 2), delta="Nothing here for now")
right_column_1.metric(label="Volatility", value = round(volatility_mkw * 100, 2), delta="Nothing here for now")



mkt_capitalization = allo.get_market_cap()




mkt_cap_plot = px.pie(mkt_capitalization, values='market_cap', names='market', title='Market Capitalization')
st.plotly_chart(mkt_cap_plot)

market_neutral_ptf = allo.market_neutral_portfolio()


left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.write("Market neutral ptf")
left_column.table(market_neutral_ptf)
right_column.write("Markowitz ptf")
right_column.table(allo.markowitz_portfolio())