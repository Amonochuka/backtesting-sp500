import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from memory_reducer import memory_reducer
from preprocessing import preprocessing
from create_signal import create_signal
from backtester import backtest


if __name__ == "__main__":
    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }

    print("=" * 50)
    print("STEP 1: Memory Reduction")
    print("=" * 50)
    prices, sp500 = memory_reducer(paths)

    print("\n" + "=" * 50)
    print("STEP 2: Preprocessing")
    print("=" * 50)
    prices, sp500 = preprocessing(prices, sp500)

    print("\n" + "=" * 50)
    print("STEP 3: Create Signal")
    print("=" * 50)
    prices = create_signal(prices)

    print("\n" + "=" * 50)
    print("STEP 4: Backtest")
    print("=" * 50)
    backtest(prices, sp500)

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETE")
    print("=" * 50)