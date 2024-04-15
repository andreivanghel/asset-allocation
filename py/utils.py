import requests
from datetime import datetime

def get_forex_value(pair: str, date: datetime, api_key: str):
    # Format date as YYYY-MM-DD string
    date_str = date.strftime('%Y-%m-%d')

    # Make API request to Alpha Vantage
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={pair[:3]}&to_symbol={pair[3:]}&apikey={api_key}"
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code != 200:
        raise ValueError("Failed to fetch forex data from Alpha Vantage")

    # Parse response JSON
    data = response.json()
    print(data)

    # Check if the date exists in the response
    if date_str not in data['Time Series FX (Daily)']:
        raise ValueError("Forex data not available for the given date")

    # Get forex value for the given date
    forex_value = data['Time Series FX (Daily)'][date_str]['4. close']

    return forex_value