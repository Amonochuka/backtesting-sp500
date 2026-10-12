import os
import sys

# Ensure scripts directory is in sys.path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from memory_reducer import memory_reducer
from preprocessing import preprocessing
from create_signal import create_signal
from backtester import backtest


def run_pipeline():
    """Execute the complete quantitative backtesting pipeline end-to-end."""
    paths = {
        'prices': os.path.join(os.path.dirname(__file__), 'data', 'stock_prices.csv'),
        'sp500': os.path.join(os.path.dirname(__file__), 'data', 'sp500.csv')
    }

    print("=" * 60)
    print("S&P 500 QUANTITATIVE STRATEGY BACKTESTING PIPELINE")
    print("=" * 60)

    print("\n" + "=" * 50)
    print("STEP 1: Memory Reduction")
    print("=" * 50)
    prices, sp500 = memory_reducer(paths)

    print("\n" + "=" * 50)
    print("STEP 2: Data Wrangling & Preprocessing")
    print("=" * 50)
    prices, sp500 = preprocessing(prices, sp500)

    print("\n" + "=" * 50)
    print("STEP 3: Momentum Signal Generation (Top 20)")
    print("=" * 50)
    prices = create_signal(prices)

    print("\n" + "=" * 50)
    print("STEP 4: Backtesting & Benchmark Evaluation")
    print("=" * 50)
    metrics = backtest(prices, sp500)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY - ALL RESULTS SAVED")
    print("=" * 60)
    return metrics


if __name__ == "__main__":
    run_pipeline()
