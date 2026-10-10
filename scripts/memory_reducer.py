import pandas as pd
import numpy as np
import os


def get_memory_usage(df: pd.DataFrame) -> float:
    """Return DataFrame memory usage in MB."""
    return df.memory_usage(deep=True).sum() / (1024 * 1024)


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize numeric column dtypes to reduce memory usage."""
    df = df.copy()

    for col in df.columns:
        col_type = df[col].dtype

        if pd.api.types.is_numeric_dtype(col_type):
            if pd.api.types.is_integer_dtype(col_type):
                df[col] = pd.to_numeric(df[col], downcast='integer')
            else:
                df[col] = df[col].astype(np.float32)

    return df


def memory_reducer(paths: dict) -> tuple:
    """
    Load CSV files, optimize dtypes, and return memory-optimized DataFrames.

    Args:
        paths: dict with keys 'prices' and 'sp500' pointing to CSV file paths

    Returns:
        Tuple of (prices_df, sp500_df) with optimized dtypes
    """
    prices_path = paths['prices']
    sp500_path = paths['sp500']

    prices = pd.read_csv(prices_path)
    sp500 = pd.read_csv(sp500_path)

    prices = prices.rename(columns={'Date': 'date'})
    sp500 = sp500[['Date', 'Adjusted Close']].rename(columns={'Date': 'date', 'Adjusted Close': 'adj_close'})
    sp500['date'] = pd.to_datetime(sp500['date'])

    print(f"Original prices memory: {get_memory_usage(prices):.2f} MB")
    print(f"Original sp500 memory: {get_memory_usage(sp500):.2f} MB")

    sp500 = optimize_dtypes(sp500)

    prices = optimize_dtypes(prices)
    sp500 = optimize_dtypes(sp500)

    print(f"Optimized prices memory: {get_memory_usage(prices):.2f} MB")
    print(f"Optimized sp500 memory: {get_memory_usage(sp500):.2f} MB")

    assert get_memory_usage(prices) < 8, "Prices dataset must be < 8MB"
    assert get_memory_usage(sp500) < 0.15, "SP500 dataset must be < 0.15MB"

    for col in prices.select_dtypes(include=[np.floating]).columns:
        assert prices[col].dtype == np.float32, f"Float column {col} not float32"

    for col in sp500.select_dtypes(include=[np.floating]).columns:
        assert sp500[col].dtype == np.float32, f"Float column {col} not float32"

    return prices, sp500


if __name__ == "__main__":
    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }
    prices, sp500 = memory_reducer(paths)
    print("memory_reducer.py executed successfully")