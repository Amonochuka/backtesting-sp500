import pandas as pd
import numpy as np


def create_signal(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Generate stock-picking signal based on 12-month historical performance:
    1. Compute average_return_1y: rolling mean of monthly_past_return over previous 12 months,
       grouped by company (12 consecutive rows).
    2. Compute signal: True if average_return_1y is among the 20 highest within the same month.
       Rank 1 is the highest metric.

    Args:
        prices: Preprocessed prices DataFrame with multi-index (date, ticker)

    Returns:
        DataFrame with new columns 'average_return_1y' and 'signal'
    """
    df = prices.copy()

    date_level = 'date' if 'date' in df.index.names else 0
    ticker_level = 'ticker' if 'ticker' in df.index.names else 1

    # Group by company to compute 12-month rolling mean of past returns
    df = df.sort_index(level=[ticker_level, date_level])
    df['average_return_1y'] = (
        df.groupby(level=ticker_level)['monthly_past_return']
        .rolling(window=12, min_periods=12)
        .mean()
        .droplevel(0)
    )

    # Sort back by date and ticker
    df = df.sort_index(level=[date_level, ticker_level])

    # Rank within each month (highest metric gets rank 1)
    df['rank'] = (
        df.groupby(level=date_level)['average_return_1y']
        .rank(ascending=False, method='first')
    )

    # Signal is True for top 20 within the month
    df['signal'] = df['rank'] <= 20
    df = df.drop(columns=['rank'])

    return df


if __name__ == "__main__":
    from memory_reducer import memory_reducer
    from preprocessing import preprocessing

    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }
    prices, sp500 = memory_reducer(paths)
    prices, sp500 = preprocessing(prices, sp500)
    prices = create_signal(prices)
    print("Signal creation completed successfully")
    print(prices.head())
    print("\nSignal value counts:")
    print(prices['signal'].value_counts())
