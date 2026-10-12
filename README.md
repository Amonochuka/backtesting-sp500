# S&P 500 Quantitative Momentum Backtesting

An end-to-end quantitative trading backtest pipeline developed for historical S&P 500 constituents (2000–2014), comparing a 12-month momentum stock-picking strategy (**Stock Picking 20**) against the buy-and-hold **S&P 500 index benchmark**.

---

## 1. Project Overview

Quantitative analysts at hedge funds evaluate equity selection strategies using retrospective simulation on historical time-series data. This project addresses the challenge of building a robust backtesting framework using real-world, messy equity datasets.

### Key Objectives
- **Memory Optimization:** Downcast large financial datasets (`stock_prices.csv` < 8MB, `sp500.csv` < 0.15MB) using minimal precision thresholds (`np.float32`).
- **Data Wrangling & Cleaning:** Handle missing data, resample to monthly frequency (`ME`), filter extreme price multiplier corruptions ($0.10 to $10,000 range), and clean return outliers with an exception for the 2008–2009 global financial crisis.
- **Signal Construction:** Compute 12-month rolling momentum (`average_return_1y`) per company and select the top 20 highest-momentum stocks each month.
- **Vectorized Backtesting:** Simulate strategy performance without iterative loops, compute monthly and cumulative Profit & Loss (PnL), and validate that total historical PnL remains bounded (< $75).
- **Benchmark Evaluation:** Compare strategy performance against an equivalent monthly capital allocation ($20/month) in the S&P 500 index.

---

## 2. Repository Structure

```
backtesting-sp500/
├── README.md
├── requirements.txt
├── main.py
├── data/
│   ├── sp500.csv
│   └── stock_prices.csv
├── notebook/
│   └── analysis.ipynb
├── scripts/
│   ├── memory_reducer.py
│   ├── preprocessing.py
│   ├── create_signal.py
│   ├── backtester.py
│   └── main.py
└── results/
    ├── outliers.txt
    ├── results.txt
    ├── cumulative_performance.png
    └── plots/
        ├── average_price_over_time.png
        ├── cumulative_performance.png
        └── missing_values_per_year.png
```

---

## 3. Installation & Environment Setup

To run the project from an empty environment:

```bash
# 1. Clone the repository
git clone https://learn.zone01kisumu.ke/git/aochuka/backtesting-sp500.git
cd backtesting-sp500

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip and install required dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Execute the full end-to-end pipeline
python main.py
```

Alternatively, you can run the pipeline from the `scripts/` directory:
```bash
python scripts/main.py
```

To run the exploratory data analysis notebook:
```bash
jupyter notebook notebook/analysis.ipynb
```

---

## 4. Python Scripts Architecture

| File | Purpose | Key Responsibilities |
| :--- | :--- | :--- |
| `scripts/memory_reducer.py` | Memory Reduction (Part 1) | Iterates over numeric columns, detects integer/float ranges, and downcasts to minimal types (`np.float32` for floats). Reduces prices from 15.3MB to 7.75MB (< 8MB) and S&P 500 from 0.06MB to 0.04MB (< 0.15MB). |
| `scripts/preprocessing.py` | Data Cleaning & Wrangling (Part 2) | Resamples data to month-end (`ME`). Removes price spikes outside [$0.10, $10,000]. Melts into multi-index `(date, ticker)`. Calculates past and future monthly returns per company independently. Replaces return outliers (> 100% or < -50%) with NaN (excluding crisis years 2008–2009). Forward-fills and drops missing values. |
| `scripts/create_signal.py` | Signal Generation (Part 3) | Calculates `average_return_1y` as the 12-month rolling mean of historical monthly returns for each company. Generates boolean column `signal = True` for the 20 highest-ranking stocks each month. |
| `scripts/backtester.py` | Strategy Backtesting (Part 4) | Vectorially computes strategy PnL (`signal * monthly_future_return`) and return (`pnl / signal.sum()`). Implements the $20/month S&P 500 benchmark. Computes cumulative PnL via `cumsum()`. Validates PnL < $75. Generates `results/results.txt` and `results/plots/cumulative_performance.png`. |
| `scripts/main.py` / `main.py` | Pipeline Orchestrator (Part 5) | Orchestrates the entire pipeline end-to-end from raw data ingestion to final backtest outputs without errors. |

---

## 5. Exploratory Data Analysis & Outliers Summary

Detailed analysis is documented in `notebook/analysis.ipynb` and `results/outliers.txt`:

1. **Extreme Multiplier Corruptions:**
   - **SPLS (Staples, Inc.)**: Reported as **$11,725,800.00** on 2000-12-12 (actual ~$11.75; 1,000,000x integer multiplier error).
   - **CSC (Computer Sciences Corp.)**: Reported as **$611,308.01** on 2014-12-30 (actual ~$64.25; 10,000x decimal shift).
   - **STT (State Street Corp.)**: Reported as **$593,809.01** on 2014-12-26 (actual ~$78.50).
   - **TMK (Torchmark Corp.)**: Reported as **$483,954.38** on 2014-12-30 (actual ~$54.10).
   - **SWY (Safeway Inc.)**: Reported as **$104,693.31** on 2014-12-19 (actual ~$34.50).
2. **Zero Price Anomalies:** Multiple constituents (e.g. CSC, ACI) had initial intervals recorded at `$0.00`.
3. **Filtering Impact:** Filtering values outside [$0.10, $10,000] and return spikes outside [-50%, +100%] prevented catastrophic skewness in aggregate time series.

---

## 6. Strategy Performance Conclusion

The backtest was executed across **157 monthly periods** from December 31, 2001 to December 31, 2014 with $20 invested each month ($1 per stock across 20 stocks):

| Metric | Stock Picking 20 Strategy | S&P 500 Benchmark | Outperformance |
| :--- | :---: | :---: | :---: |
| **Total Capital Invested** | $3,140.00 | $3,140.00 | — |
| **Total Net PnL** | **$66.14** | **$15.00** | **+$51.14** |
| **Total Strategy Return** | **2.11%** | **0.48%** | **+1.63%** |
| **Average Monthly Return** | **2.11%** | **0.48%** | **+1.63%** |
| **Annualized Sharpe Ratio** | **1.00** | **0.39** | **+0.61** |
| **Historical PnL Limit Check** | **Passed** ($66.14 < $75.00) | — | Validated |

### Key Takeaways
1. **Significant Alpha:** The momentum-based Stock Picking 20 strategy generated **4.41x the net profit** of the broad S&P 500 index ($66.14 vs $15.00), demonstrating persistent momentum premium among top past performers.
2. **Superior Risk-Adjusted Returns:** With an annualized Sharpe Ratio of **1.00** compared to **0.39** for the benchmark, the strategy provided superior risk-adjusted compensation.
3. **Data Quality Sensitivity:** Effective preprocessing and bounded outlier clipping are essential prerequisites for quantitative backtesting; uncorrected outliers would have caused arbitrary billions of dollars in fake returns.
