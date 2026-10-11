import pandas as pd
import numpy as np


def resample_monthly_last(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """Resample DataFrame to monthly frequency, keeping last value of each month."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    try:
        df = df.resample('ME').last()
    except Exception:
        df = df.resample('M').last()
    df = df.reset_index()
    return df


def filter_price_outliers(df: pd.DataFrame, price_cols: list, min_price: float = 0.1, max_price: float = 10000.0) -> pd.DataFrame:
    """Filter out price outliers outside the specified range [min_price, max_price]."""
    df = df.copy()
    for col in price_cols:
        if col in df.columns:
            df[col] = df[col].where((df[col] >= min_price) & (df[col] <= max_price))
    return df


def melt_prices(prices: pd.DataFrame, price_cols: list) -> pd.DataFrame:
    """Convert wide format prices to long format with multi-index (date, ticker)."""
    date_col = 'date'
    melted = prices.melt(id_vars=[date_col], value_vars=price_cols,
                         var_name='ticker', value_name='Price')
    melted[date_col] = pd.to_datetime(melted[date_col])
    melted = melted.set_index([date_col, 'ticker']).sort_index()
    return melted


def compute_returns_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute past and future returns in long format per company independently.
    Past: return(current month) = (price(current month) - price(previous month)) / price(previous month)
    Future: return(current month) = (price(next month) - price(current month)) / price(current month)
    """
    df = df.copy()
    df = df.sort_index(level=['ticker', 'date'])
    prev_price = df.groupby(level='ticker')['Price'].shift(1)
    next_price = df.groupby(level='ticker')['Price'].shift(-1)
    df['monthly_past_return'] = (df['Price'] - prev_price) / prev_price
    df['monthly_future_return'] = (next_price - df['Price']) / df['Price']
    df = df.sort_index(level=['date', 'ticker'])
    return df


def filter_return_outliers_long(df: pd.DataFrame, year_exception: list = None) -> pd.DataFrame:
    """Filter return outliers per company (> 1 or < -0.5), with exception for 2008 and 2009."""
    df = df.copy()
    if year_exception is None:
        year_exception = [2008, 2009]

    for col in ['monthly_past_return', 'monthly_future_return']:
        year_mask = df.index.get_level_values(0).year.isin(year_exception)
        outlier_mask = (df[col] > 1.0) | (df[col] < -0.5)
        df.loc[outlier_mask & ~year_mask, col] = np.nan
    return df


def forward_fill_per_company_long(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Forward fill missing values within each company independently."""
    df = df.copy()
    df = df.sort_index(level=['ticker', 'date'])
    for col in cols:
        df[col] = df.groupby(level='ticker')[col].ffill()
    df = df.sort_index(level=['date', 'ticker'])
    return df


def drop_remaining_nan(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with any remaining NaN values."""
    return df.dropna()


def verify_no_missing(df: pd.DataFrame) -> bool:
    """Verify that there are no missing values in the DataFrame."""
    missing = df.isnull().sum().sum()
    assert missing == 0, f"Found {missing} missing values"
    return True


def preprocess_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Full preprocessing pipeline for stock prices."""
    prices = prices.copy()
    price_cols = [c for c in prices.columns if c != 'date']

    prices = resample_monthly_last(prices, 'date')
    prices = filter_price_outliers(prices, price_cols)

    melted = melt_prices(prices, price_cols)
    melted = compute_returns_long(melted)
    melted = filter_return_outliers_long(melted)
    melted = forward_fill_per_company_long(melted, ['monthly_past_return', 'monthly_future_return'])
    melted = drop_remaining_nan(melted)
    verify_no_missing(melted)

    return melted[['Price', 'monthly_past_return', 'monthly_future_return']]


def preprocess_sp500(sp500: pd.DataFrame) -> pd.DataFrame:
    """Preprocess SP500 index data with monthly historical returns."""
    sp500 = sp500.copy()
    sp500 = resample_monthly_last(sp500, 'date')
    sp500['sp500_return'] = sp500['adj_close'].pct_change()
    sp500 = sp500.dropna()
    return sp500[['date', 'sp500_return']]


def preprocessing(prices: pd.DataFrame, sp500: pd.DataFrame) -> tuple:
    """
    Main preprocessing function.

    Args:
        prices: Raw stock prices DataFrame
        sp500: Raw SP500 index DataFrame

    Returns:
        Tuple of (processed_prices, processed_sp500)
    """
    processed_prices = preprocess_prices(prices)
    processed_sp500 = preprocess_sp500(sp500)
    return processed_prices, processed_sp500


if __name__ == "__main__":
    from memory_reducer import memory_reducer

    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }
    prices, sp500 = memory_reducer(paths)
    prices, sp500 = preprocessing(prices, sp500)
    print("Preprocessing completed successfully")
    print(f"Prices shape: {prices.shape}")
    print(f"SP500 shape: {sp500.shape}")
    print(prices.head())
    print(sp500.head())
