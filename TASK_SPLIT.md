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

## Difficulty Assessment (for fair split)

| File | Difficulty | Reason |
|------|------------|--------|
| `preprocessing.py` | **HEAVY** | 8+ steps: resample, 2 return calcs, outlier filter w/ 2008-09 exception, per-group ffill, verification |
| `analysis.ipynb` | **HEAVY** | Full EDA + manual research for 5 outliers cross-referenced externally |
| `backtester.py` | **HEAVY** | Vectorized PnL, benchmark, cumsum, validation (PnL<$75), plotting, file output |
| `memory_reducer.py` | **MEDIUM** | Column iteration, dtype detection, downcasting logic |
| `create_signal.py` | **MEDIUM** | Rolling 12M avg + groupby rank within month |
| `main.py` | **LIGHT** | Pipeline wiring only |
| `requirements.txt` | **TRIVIAL** | List dependencies |
| `README.md` | **LIGHT** | Document after results exist |
| `results/` folder | **TRIVIAL** | mkdir |
| Data setup | **TRIVIAL** | Download CSVs |

---

## Task Assignment (Balanced by Difficulty)

### 🟦 **Amon Ochuka (#aochuka) - Data Pipeline Owner**

**Core Pipeline (1 HEAVY + 1 MEDIUM + 3 LIGHT)**

#### 1. `memory_reducer.py` (Part 1 - Preliminary) — MEDIUM
- [ ] Function `memory_reducer(paths)` → optimized (prices, sp500) DataFrames
- [ ] Float → `np.float32` min; integers → smallest fitting dtype
- [ ] Targets: prices < 8MB, sp500 < 0.15MB

#### 2. `preprocessing.py` (Part 2 - Core Preprocessing) — **HEAVY**
- [ ] Function `preprocessing(prices, sp500)` → cleaned (prices, sp500)
- **Prices:**
  - Monthly resample (last), sort by date
  - Filter price outliers: $0.1 – $10,000
  - Compute `monthly_past_return` = (price_t - price_t-1)/price_t-1
  - Compute `monthly_future_return` = (price_t+1 - price_t)/price_t
  - Return outliers → NaN if >1 or <-0.5 **except 2008-2009**
  - Outlier detection **per company** (groupby ticker)
  - Forward fill missing **per company**
  - Drop remaining NaN, verify 0 missing
  - Final columns: `Price`, `monthly_past_return`, `monthly_future_return`
- **SP500:** Monthly resample + historical monthly returns on adjusted close
- [ ] Modular helper functions

#### 3. `main.py` (Part 5 - Pipeline Orchestration) — LIGHT
- [ ] Wire full pipeline:
```python
prices, sp500 = memory_reducer(paths)
prices, sp500 = preprocessing(prices, sp500)
prices = create_signal(prices)
backtest(prices, sp500)
```
- [ ] Define `paths`, imports, run error-free from clean env
- [ ] Ensure all results save to `results/`

#### 4. `requirements.txt` — TRIVIAL
- [ ] pandas, numpy, matplotlib, jupyter + versions

#### 5. Data Setup — TRIVIAL
- [ ] Place `sp500.csv`, `stock_prices.csv` in `data/`
- [ ] Verify load

---

### 🟨 **Aaron Ajwoga (#aabrown) - Analysis & Strategy Owner**

**Analysis + Signal + Backtest + Docs (2 HEAVY + 1 MEDIUM + 2 LIGHT)**

#### 1. `analysis.ipynb` (Part 2 - EDA) — **HEAVY**
- [ ] **Missing values:** per variable, per year, visualization
- [ ] **Outliers:** statistical detection (IQR/z-score), price distributions
- [ ] **Visualization:** avg price over time OR price consistency across companies → save to `results/plots/`
- [ ] **5+ outliers:** cross-reference external source (Yahoo Finance), document ticker/date/price/explanation → `results/outliers.txt`
- [ ] Helper functions with `plot=False` default, titles, axis labels

#### 2. `create_signal.py` (Part 3 - Signal) — MEDIUM
- [ ] Function `create_signal(prices)` → prices with new columns:
  - `average_return_1y`: 12-month rolling mean of `monthly_past_return` per company
  - `signal`: True if `average_return_1y` rank ≤ 20 within month (rank 1 = highest)

#### 3. `backtester.py` (Part 4 - Backtest) — **HEAVY**
- [ ] Function `backtest(prices, sp500)`:
  - **Strategy:** `pnl = signal * monthly_future_return` (vectorized, no loops)
  - `strategy_return = pnl / signal.sum()` per period
  - **Benchmark:** signal = `pd.Series([20, 20, ...])` ($20/month on SP500)
  - Compute benchmark PnL & returns
  - **Cumulative:** `cumsum()` for both
  - **Validate:** full historical PnL < $75 (else outliers not fixed)
  - **Save:** `results/results.txt` with PnL & total returns for both
  - **Plot:** cumulative performance both strategies, title, legend, axis labels → `results/plots/`

#### 4. `README.md` — LIGHT
- [ ] Project description
- [ ] Run instructions (venv, pip install, python main.py)
- [ ] File summaries
- [ ] Conclusion with strategy performance (after backtest)

#### 5. Results Folder — TRIVIAL
- [ ] Create `results/plots/`
- [ ] Verify all outputs save: `results.txt`, `outliers.txt`, plots

---

## Shared Responsibilities

| Task | Owner | Notes |
|------|-------|-------|
| Code Review | Both | PRs within 4 hrs |
| Integration Testing | Both | Run `python main.py` together |
| Git Commits | Both | Own work, clear messages |
| Final Sign-off | Both | Verify acceptance criteria |

---

## Dependency Flow

```
memory_reducer.py (Amon, MEDIUM)
       ↓
preprocessing.py (Amon, HEAVY) ←→ analysis.ipynb (Aaron, HEAVY) [parallel after memory_reducer]
       ↓
create_signal.py (Aaron, MEDIUM)
       ↓
backtester.py (Aaron, HEAVY)
       ↓
main.py (Amon, LIGHT) ← integrates all
       ↓
README.md (Aaron, LIGHT) ← documents results
```

**Critical Path:** Amon's preprocessing must complete before Aaron's create_signal/backtester can be fully tested. Aaron can start analysis.ipynb in parallel after memory_reducer.

---

## Acceptance Criteria (Spec-Compliant)

- [ ] `memory_reducer.py`: prices < 8MB, sp500 < 0.15MB, float32 minimum
- [ ] `preprocessing.py`: monthly resampled, price/return outliers filtered, 2008-09 exception, per-company ops, 0 missing
- [ ] `analysis.ipynb`: 4 EDA components + 5 documented outliers
- [ ] `create_signal.py`: 12M rolling avg, top-20 monthly signal
- [ ] `backtester.py`: vectorized, benchmark, cumsum, PnL < $75, plot saved
- [ ] `main.py`: runs end-to-end error-free
- [ ] `README.md`: complete with run instructions & conclusions
- [ ] All results in `results/`

---

## Key Spec Reminders

- **Data is messy:** wrong prices, spikes, splits/dividends — fix main issues only
- **SP500 constituents change:** companies enter/exit (e.g., FB 2013)
- **No look-ahead bias:** historical vs future returns separate
- **2008-2009 exception:** NO return outlier filtering those years
- **Per-company processing:** all outlier detection & filling within ticker
- **No for loops:** backtester must be vectorized

---

## Sign-off

- Amon Ochuka: _________________________ Date: ___________
- Aaron Ajwoga: _________________________ Date: ___________