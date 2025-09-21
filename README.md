# Assignment 2: Conditional Execution — Smoking Status Analyzer (No Pandas)

This version **does not use pandas**. It uses only Python's standard library (`csv`, `argparse`, etc.).

## Purpose of this program
Practice **conditional execution** in Python while analyzing a real dataset. The script showcases `if / elif / else` logic for input checks, branching on values, and interpreting results.

## Inputs / Outputs
**Input:**
- CSV file: `smoking_health_data_final (1).csv`
- Yes/No column name: `current_smoker`
- Optional flags: `--yes`, `--no`, `--case_insensitive`

**Output:**
- Console printout with:
  - Number of "Yes"
  - Number of "No"
  - Percent "No" (of valid Yes/No responses)
  - Count of Other/Missing values
  - Interpretation line

## How to run
```bash
python analyze_smoking_nopandas.py --csv "smoking_health_data_final (1).csv" --col "current_smoker" --yes yes --no no --case_insensitive
```

## Example actual results (this dataset)
```
=== Analysis (No Pandas) ===
CSV file: smoking_health_data_final (1).csv
Column analyzed: current_smoker
Valid responses (Yes/No only): 3900
  - Number of 'yes': 1932
  - Number of 'no':  1968
  - Percent 'no':    50.46%
Other or missing values: 0
```

## Files
- `analyze_smoking_nopandas.py` — main script (no pandas)
- `results_no_pandas.txt` — saved output from a run on your dataset
