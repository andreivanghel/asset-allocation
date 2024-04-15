import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from portfolio_allocation import AllocationModel
import utils
from datetime import datetime
import json

data = pd.read_csv("/Users/andrei/Documents/asset-allocation-data/processed/2024-02-25/equities_2024-02-25.csv")
data['DATE'] = pd.to_datetime(data['DATE'])

with open("/Users/andrei/Documents/GitHub/asset-allocation/market_capitalization.JSON", 'r') as mkt_cap_json:
    mkt_cap = json.load(mkt_cap_json)


allo = AllocationModel(data, mkt_cap)

expected_returns_mkw = allo.get_Portfolio_Return(allo.markowitz_portfolio())
volatility_mkw = allo.get_Portfolio_Volatility(allo.markowitz_portfolio())

pair = "EURUSD"
date = datetime(2024, 3, 29)
api_key = "Y73MRQV5EGUOELUU"
#forex_value = utils.get_forex_value(pair, date, api_key)

st.metric(label="Expected returns", value = expected_returns_mkw, delta="Nothing here for now")
st.metric(label="Volatility", value = volatility_mkw, delta="Nothing here for now")
#st.metric(label=pair, value = forex_value, delta = "Test, FOREX method")


### checkbox test
if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data


### selectbox test
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', option


left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button('Press me!')

# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        'Sorting hat',
        ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"))
    st.write(f"You are in {chosen} house!")