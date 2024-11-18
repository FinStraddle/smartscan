import pandas as pd

def process_stock_data(data):
    """
    Process the fetched stock data
    :param data: Dictionary of DataFrames with stock data
    :return: Processed data
    """
    processed_data = {}
    for symbol, df in data.items():
        # Basic data cleaning and processing
        df = df.dropna()
        df['Returns'] = df['Close'].pct_change()
        processed_data[symbol] = df

    return processed_data