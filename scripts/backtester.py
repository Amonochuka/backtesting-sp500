import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def backtest(prices: pd.DataFrame, sp500: pd.DataFrame, results_dir: str = 'results') -> dict:
    """
    Backtest the stock picking strategy against the SP500 benchmark:
    1. Compute PnL by multiplying signal Series by future returns (vectorized, no for loop).
    2. Compute return of the strategy by dividing PnL by sum of signal Series.
    3. For SP500 benchmark, invest $20 each month: signal = pd.Series([20, 20, ..., 20]).
    4. Compute cumulative PnL using cumsum for both strategies.
    5. Verify full historical PnL is smaller than $75.
    6. Save PnL and total returns to results/results.txt.
    7. Generate and save cumulative performance comparison plot.

    Args:
        prices: DataFrame with multi-index (date, ticker), columns 'signal' and 'monthly_future_return'
        sp500: DataFrame with SP500 data and 'sp500_return'
        results_dir: Output directory for results and plots

    Returns:
        dict containing metrics and summary statistics
    """
    print("\n--- Starting Vectorized Backtest ---")
    prices = prices.copy()

    # 1. Strategy PnL: signal * future_return without for loops
    prices['pnl'] = prices['signal'].astype(int) * prices['monthly_future_return']

    date_level = 'date' if 'date' in prices.index.names else 0
    strategy_monthly_pnl = prices.groupby(level=date_level)['pnl'].sum()
    strategy_monthly_signals = prices.groupby(level=date_level)['signal'].sum()

    # Identify active investment periods where signals are present
    active_dates = strategy_monthly_signals[strategy_monthly_signals > 0].index
    strategy_active_pnl = strategy_monthly_pnl.loc[active_dates]
    total_signals = prices['signal'].sum()
    total_strategy_pnl = prices['pnl'].sum()
    strategy_total_return = total_strategy_pnl / total_signals if total_signals > 0 else 0.0

    # 2. SP500 Benchmark: signal = 20 each month
    if 'date' in sp500.columns:
        sp500_series = sp500.set_index('date')['sp500_return']
    else:
        sp500_series = sp500['sp500_return']

    common_dates = active_dates.intersection(sp500_series.index)
    strat_pnl_aligned = strategy_active_pnl.loc[common_dates]
    sp500_ret_aligned = sp500_series.loc[common_dates]

    # Benchmark signal: 20 dollars invested per month
    benchmark_signal = pd.Series(20.0, index=common_dates, name='sp500_signal')
    benchmark_monthly_pnl = benchmark_signal * sp500_ret_aligned
    total_benchmark_pnl = benchmark_monthly_pnl.sum()
    total_benchmark_invested = benchmark_signal.sum()
    benchmark_total_return = total_benchmark_pnl / total_benchmark_invested if total_benchmark_invested > 0 else 0.0

    # 3. Cumulative PnL using cumsum()
    strategy_cum_pnl = strat_pnl_aligned.cumsum()
    benchmark_cum_pnl = benchmark_monthly_pnl.cumsum()

    # 4. Acceptance validation: full historical PnL must be smaller than $75
    print(f"Stock Picking 20 Total PnL: ${total_strategy_pnl:.4f}")
    print(f"Stock Picking 20 Total Return: {strategy_total_return * 100:.2f}%")
    print(f"SP500 Benchmark Total PnL: ${total_benchmark_pnl:.4f}")
    print(f"SP500 Benchmark Total Return: {benchmark_total_return * 100:.2f}%")

    assert total_strategy_pnl < 75.0, (
        f"Validation failed: Strategy PnL ${total_strategy_pnl:.2f} >= $75 limit. "
        "Outliers were not corrected properly."
    )
    print("✓ Validation passed: Strategy PnL is smaller than $75.")

    # 5. Save results to results/results.txt
    plots_dir = os.path.join(results_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    header_line = "=" * 65 + "\n"
    results_file = os.path.join(results_dir, 'results.txt')
    lines = [
        header_line,
        "BACKTEST PERFORMANCE SUMMARY: STOCK PICKING 20 vs S&P 500\n",
        header_line,
        "\n",
        f"Backtest Period:           {common_dates.min().strftime('%Y-%m-%d')} to {common_dates.max().strftime('%Y-%m-%d')}\n",
        f"Number of Months:          {len(common_dates)}\n",
        f"Monthly Capital Invested:  $20.00\n\n",
        "1. Stock Picking 20 Strategy:\n",
        f"   Total Invested:         ${total_signals:.2f}\n",
        f"   Total Net PnL:          ${total_strategy_pnl:.4f}\n",
        f"   Total Return:           {strategy_total_return * 100:.2f}%\n",
        f"   Average Monthly Return: {(strat_pnl_aligned / 20.0).mean() * 100:.2f}%\n",
        f"   Monthly Return Vol:     {(strat_pnl_aligned / 20.0).std() * 100:.2f}%\n",
        f"   Sharpe Ratio (Rf=0%):   {((strat_pnl_aligned / 20.0).mean() / (strat_pnl_aligned / 20.0).std()) * np.sqrt(12):.2f}\n\n",
        "2. S&P 500 Benchmark Strategy:\n",
        f"   Total Invested:         ${total_benchmark_invested:.2f}\n",
        f"   Total Net PnL:          ${total_benchmark_pnl:.4f}\n",
        f"   Total Return:           {benchmark_total_return * 100:.2f}%\n",
        f"   Average Monthly Return: {sp500_ret_aligned.mean() * 100:.2f}%\n",
        f"   Monthly Return Vol:     {sp500_ret_aligned.std() * 100:.2f}%\n",
        f"   Sharpe Ratio (Rf=0%):   {(sp500_ret_aligned.mean() / sp500_ret_aligned.std()) * np.sqrt(12):.2f}\n\n",
        "3. Comparison & Outperformance:\n",
        f"   Excess Net PnL:         +${total_strategy_pnl - total_benchmark_pnl:.4f}\n",
        f"   Return Difference:      +{(strategy_total_return - benchmark_total_return) * 100:.2f}%\n",
        f"   Outperformance Factor:  {total_strategy_pnl / total_benchmark_pnl:.2f}x\n",
        header_line
    ]

    with open(results_file, 'w') as f:
        f.writelines(lines)
    print(f"Saved performance results to {results_file}")

    # 6. Plot cumulative performance
    plot_path = os.path.join(plots_dir, 'cumulative_performance.png')
    root_plot_path = os.path.join(results_dir, 'cumulative_performance.png')

    plt.figure(figsize=(12, 6))
    plt.plot(strategy_cum_pnl.index, strategy_cum_pnl.values, label='Stock Picking 20 Strategy', color='#10b981', linewidth=2)
    plt.plot(benchmark_cum_pnl.index, benchmark_cum_pnl.values, label='S&P 500 Benchmark', color='#6366f1', linewidth=2, linestyle='--')
    plt.title('Cumulative Performance: Stock Picking 20 vs S&P 500 Benchmark', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Profit & Loss ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=11, loc='upper left')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.savefig(root_plot_path, dpi=150)
    plt.close()
    print(f"Saved cumulative performance plot to {plot_path}")

    return {
        'strategy_total_pnl': total_strategy_pnl,
        'strategy_total_return': strategy_total_return,
        'benchmark_total_pnl': total_benchmark_pnl,
        'benchmark_total_return': benchmark_total_return,
        'strategy_cum_pnl': strategy_cum_pnl,
        'benchmark_cum_pnl': benchmark_cum_pnl
    }


if __name__ == "__main__":
    from memory_reducer import memory_reducer
    from preprocessing import preprocessing
    from create_signal import create_signal

    paths = {
        'prices': 'data/stock_prices.csv',
        'sp500': 'data/sp500.csv'
    }
    prices, sp500 = memory_reducer(paths)
    prices, sp500 = preprocessing(prices, sp500)
    prices = create_signal(prices)
    metrics = backtest(prices, sp500)
    print("Backtest executed successfully!")
