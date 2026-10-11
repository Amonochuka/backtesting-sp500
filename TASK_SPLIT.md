# Task Split Document: Backtesting SP500 Project

**Project:** backtesting-sp500  
**Team Members:** Amon Ochuka (#aochuka), Aaron Ajwoga (#aabrown)  
**Date:** 2026-10-11  
**Repo:** https://learn.zone01kisumu.ke/git/aochuka/backtesting-sp500

---

## Project Structure to Create

```
project/
│   README.md
│   requirements.txt
│
└───data/
│   │   sp500.csv
│   │   stock_prices.csv
│
└───notebook/
│   │   analysis.ipynb
│
└───scripts/
│   │   memory_reducer.py
│   │   preprocessing.py
│   │   create_signal.py
│   │   backtester.py
│   │   main.py
│
└───results/
    │   plots/
    │   results.txt
    │   outliers.txt
```

---

## Task Assignment

### 🟦 Amon Ochuka (#aochuka) - Data Engineering & Pipeline Integration

#### 1. **memory_reducer.py** (Part 1 - Preliminary)
- [ ] Create `memory_reducer.py` with function `memory_reducer(paths)` that:
  - Takes CSV file paths as input
  - Optimizes dtypes to reduce memory usage
  - Returns memory-optimized DataFrames for both prices and sp500
  - Float columns → `np.float32` (minimum, preserve precision)
  - Integer columns → smallest fitting dtype (int8, int16, int32, int64)
  - Optimized prices dataset < 8MB
  - Optimized sp500 dataset < 0.15MB
- [ ] Implementation steps:
  - Iterate over every column
  - Determine if numeric
  - Determine if integer-representable
  - Find min/max values
  - Apply smallest fitting dtype

#### 2. **preprocessing.py** (Part 2 - Data Preprocessing Logic)
- [ ] Create `preprocessing.py` with function `preprocessing(prices, sp500)` that:
  - **Prices DataFrame:**
    - Resample to monthly frequency, keep last value (month-end)
    - Sort by date
    - Filter price outliers: remove prices outside $0.1 to $10,000
    - Compute monthly returns:
      - Historical: `(price_t - price_t-1) / price_t-1`
      - Future: `(price_t+1 - price_t) / price_t`
    - Replace return outliers with NaN:
      - Returns > 1 or < -0.5 → NaN
      - **Exception:** Do NOT filter years 2008 and 2009 (financial crisis)
      - Outlier detection per company (groupby ticker)
    - Forward fill missing values within each company independently
    - Drop remaining NaN values
    - Verify zero missing values
    - Final columns: `Price`, `monthly_past_return`, `monthly_future_return`
  - **SP500 DataFrame:**
    - Resample to monthly frequency, keep last value
    - Compute historical monthly returns on adjusted close
- [ ] Helper functions for each sub-step (modular design)

#### 3. **main.py** (Part 5 - Main Pipeline)
- [ ] Create `main.py` that executes full pipeline:
```python
# import data
prices, sp500 = memory_reducer(paths)

# preprocessing
prices, sp500 = preprocessing(prices, sp500)

# create signal
prices = create_signal(prices)

# backtest
backtest(prices, sp500)
```
- [ ] Define `paths` to data files
- [ ] Import functions from other modules
- [ ] Run without errors from empty environment
- [ ] Save all results to `results/` folder

#### 4. **requirements.txt**
- [ ] List all dependencies with versions:
  - pandas
  - numpy
  - matplotlib
  - jupyter (for notebook)
  - Any others used

#### 5. **Data Folder Setup**
- [ ] Download/place `sp500.csv` and `stock_prices.csv` in `data/`
- [ ] Verify data loads correctly

---

### 🟨 Aaron Ajwoga (#aabrown) - Analysis, Signal & Backtesting

#### 1. **analysis.ipynb** (Part 2 - Exploratory Data Analysis)
- [ ] Create Jupyter Notebook `notebook/analysis.ipynb` with:
  - **Missing Values Analysis:**
    - Count missing values per variable
    - Count missing values per year
    - Visualize missingness patterns
  - **Outliers Analysis:**
    - Statistical outlier detection (IQR, z-score)
    - Price distribution analysis
  - **Visualization:**
    - Plot: Average price for companies over time **OR** price consistency across companies
    - Save plot to `results/plots/`
    - All plots: titles, axis labels, parameter `plot=False` (default) to suppress display
  - **Outlier Identification (5+ outliers):**
    - Cross-reference with external source (Yahoo Finance, etc.)
    - Document: ticker, date, price, explanation
    - Save to `results/outliers.txt`
- [ ] Create helper functions in notebook that generate plots and save to `results/plots/`

#### 2. **create_signal.py** (Part 3 - Signal Creation)
- [ ] Create `create_signal.py` with function `create_signal(prices)` that:
  - **average_return_1y column:** Average of `monthly_past_return` over previous 12 months (12 consecutive rows), grouped by company
  - **signal column:** Boolean, `True` if `average_return_1y` is among top 20 highest within same month
    - Rank 1 = highest metric
    - Use `groupby('date').rank(ascending=False)` or similar
    - Signal = True where rank <= 20

#### 3. **backtester.py** (Part 4 - Backtesting)
- [ ] Create `backtester.py` with function `backtest(prices, sp500)` that:
  - **Strategy PnL:**
    - `pnl = signal * monthly_future_return` (vectorized, no for loops)
    - `strategy_return = pnl / signal.sum()` (per period)
  - **SP500 Benchmark:**
    - Signal = `pd.Series([20, 20, ..., 20])` (invest $20/month on SP500)
    - Compute benchmark PnL and returns
  - **Cumulative PnL:**
    - `cumsum()` for both strategies
  - **Validation:**
    - Full historical PnL < $75 (if not, outliers not corrected properly)
  - **Save Results:**
    - `results/results.txt` with PnL and total returns for both strategies
  - **Plot:**
    - Cumulative performance over time for both strategies
    - Title, legend, x-axis label, y-axis label
    - Save to `results/plots/`

#### 4. **README.md**
- [ ] Create comprehensive README.md with:
  - Project description
  - Instructions to run from empty environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python main.py
    ```
  - Summary of each Python file's purpose
  - Conclusion: Strategy performance summary (after backtest runs)

#### 5. **Results Folder Structure**
- [ ] Create `results/plots/` directory
- [ ] Ensure all outputs save correctly:
  - `results/results.txt`
  - `results/outliers.txt`
  - `results/plots/*.png`

---

## Shared Responsibilities

| Task | Owner | Notes |
|------|-------|-------|
| Code Review | Both | Review each other's PRs |
| Testing | Both | Run `python main.py` together |
| Git Commits | Both | Commit own work with clear messages |
| Final Integration | Amon | Ensure pipeline runs end-to-end |

---

## Dependencies Between Tasks

```
memory_reducer.py (Amon)
       ↓
preprocessing.py (Amon) ← analysis.ipynb (Aaron) [parallel, but analysis informs preprocessing]
       ↓
create_signal.py (Aaron)
       ↓
backtester.py (Aaron)
       ↓
main.py (Amon) ← integrates all
       ↓
README.md (Aaron) ← documents results
```

**Critical Path:** Amon's tasks (1→2→5) must complete before Aaron's tasks (3→4) can be fully tested, but Aaron can work on 1 & 2 in parallel.

---

## Communication Protocol

- **Daily Sync:** 15 min standup to discuss progress/blockers
- **PR Reviews:** Within 4 hours of creation
- **Blocking Issues:** Slack/Teams immediately
- **Definition of Done:** Code runs, tests pass, results saved, documented

---

## Acceptance Criteria (Per Spec)

- [ ] `memory_reducer.py`: Prices < 8MB, SP500 < 0.15MB, float32 minimum
- [ ] `preprocessing.py`: Monthly resampled, outliers filtered, returns computed, 0 missing values
- [ ] `analysis.ipynb`: All 4 EDA components + 5 outliers documented
- [ ] `create_signal.py`: 12-month avg return, top-20 monthly signal
- [ ] `backtester.py`: Vectorized PnL, benchmark comparison, cumulative plot, PnL < $75
- [ ] `main.py`: Runs end-to-end without errors
- [ ] `README.md`: Complete with run instructions and conclusions
- [ ] All results saved to `results/` folder structure

---

## Notes

- **Data Quality:** Expect messy data (wrong prices, spikes, splits/dividends). Correct main problems only.
- **SP500 Constituents Change:** Companies enter/exit over time (e.g., Facebook entered 2013).
- **Look-ahead Bias:** Historical vs future returns must be separate.
- **2008-2009 Exception:** Do not filter return outliers during financial crisis.
- **Per-Company Processing:** All outlier detection and filling done within each ticker independently.
- **No For Loops:** Backtesting must use vectorized pandas operations.

---

**Sign-off:**

- Amon Ochuka: _________________________ Date: ___________
- Aaron Ajwoga: _________________________ Date: ___________