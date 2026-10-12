import os
import pandas as pd
import numpy as np
from typing import Union


def get_memory_usage(df: pd.DataFrame) -> float:
    """Return DataFrame memory usage in MB."""
    return df.memory_usage(deep=True).sum() / (1024 * 1024)


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize numeric column dtypes to reduce memory usage:
    - Iterate over every column
    - Determine if the column is numeric
    - Determine if the column can be represented by an integer
    - Find min and max values
    - Apply smallest datatype that fits range (np.float32 minimum for floats)
    """
    df = df.copy()

    for col in df.columns:
        col_type = df[col].dtype

        if pd.api.types.is_numeric_dtype(col_type):
            if pd.api.types.is_integer_dtype(col_type):
                df[col] = pd.to_numeric(df[col], downcast='integer')
            else:
                # For floating-point data, the smallest data type used must be np.float32
                df[col] = df[col].astype(np.float32)

    return df


def memory_reducer(input_data: Union[str, dict]) -> Union[pd.DataFrame, tuple]:
    """
    Load CSV file(s), optimize types to reduce memory usage, and return optimized DataFrame(s).

    Supports:
    1. Single CSV file path (str): returns single memory-optimized DataFrame.
    2. Dict of paths (dict): e.g. {'prices': 'path', 'sp500': 'path'}, returns (prices_df, sp500_df).
    """
    if isinstance(input_data, str):
        df = pd.read_csv(input_data)
        if 'Date' in df.columns:
            df = df.rename(columns={'Date': 'date'})
        if 'Adjusted Close' in df.columns:
            df = df.rename(columns={'Adjusted Close': 'adj_close'})
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        initial_mem = get_memory_usage(df)
        df = optimize_dtypes(df)
        optimized_mem = get_memory_usage(df)
        print(f"Memory reduction ({os.path.basename(input_data)}): {initial_mem:.2f} MB -> {optimized_mem:.2f} MB")
        return df

    elif isinstance(input_data, dict):
        prices_path = input_data['prices']
        sp500_path = input_data['sp500']

        prices = pd.read_csv(prices_path)
        sp500 = pd.read_csv(sp500_path)

        prices = prices.rename(columns={'Date': 'date'})
        sp500 = sp500[['Date', 'Adjusted Close']].rename(columns={'Date': 'date', 'Adjusted Close': 'adj_close'})
        sp500['date'] = pd.to_datetime(sp500['date'])

        print(f"Original prices memory: {get_memory_usage(prices):.2f} MB")
        print(f"Original sp500 memory: {get_memory_usage(sp500):.2f} MB")

        prices = optimize_dtypes(prices)
        sp500 = optimize_dtypes(sp500)

        print(f"Optimized prices memory: {get_memory_usage(prices):.2f} MB")
        print(f"Optimized sp500 memory: {get_memory_usage(sp500):.2f} MB")

        assert get_memory_usage(prices) < 8.0, "Prices dataset must be < 8MB"
        assert get_memory_usage(sp500) < 0.15, "SP500 dataset must be < 0.15MB"

        for col in prices.select_dtypes(include=[np.floating]).columns:
            assert prices[col].dtype == np.float32, f"Float column {col} not float32"

        for col in sp500.select_dtypes(include=[np.floating]).columns:
            assert sp500[col].dtype == np.float32, f"Float column {col} not float32"

        return prices, sp500
    else:
        raise TypeError(f"Expected str or dict, got {type(input_data)}")


if __name__ == "__main__":
    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }
    prices, sp500 = memory_reducer(paths)
    print("memory_reducer.py executed successfully")
