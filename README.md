# Assignment 2: Conditional Execution — Smoking Status Analyzer

## Purpose of this program
Practice **conditional execution** in Python while analyzing a real dataset. The script demonstrates `if / elif / else` logic for validating inputs, branching on values, and interpreting results.

## What the program does (inputs/outputs)
**Input:**
- A CSV file containing survey responses (e.g., `smoking_health_data_final (1).csv`).
- The name of a column that represents a yes/no question (e.g., `current_smoker`).
- Optional flags to customize the “yes” and “no” labels (e.g., `Y`/`N`, `True`/`False`) and to compare case-insensitively.

**Process:**
- Checks that the specified column exists.
- Iterates over rows and classifies them into **Yes**, **No**, or **Other/Missing** using conditional logic.
- Computes:
  - The **number** of participants who said **Yes**
  - The **percent** who said **No** (out of valid Yes/No responses)

**Output:**
- Counts and percentage printed to the console.
- A brief interpretation (e.g., majority No, more Yes than No, or balanced).

## How to use the program
1. Place your CSV file in the project folder (or note its path).
2. Run:
   ```bash
   python analyze_smoking.py --csv "smoking_health_data_final (1).csv" --col "current_smoker" --yes yes --no no --case_insensitive
   ```
3. Read the console output for:
   - Number of “Yes”
   - Percent “No”
   - Any notes about missing/other values
   - A short interpretation

## Example actual run (this dataset)
**Command:**
```bash
python analyze_smoking.py --csv "smoking_health_data_final (1).csv" --col "current_smoker" --yes yes --no no --case_insensitive
```

**Output:**
```
=== Analysis ===
CSV file: smoking_health_data_final (1).csv
Column analyzed: current_smoker
YES label: 'yes', NO label: 'no'
Valid responses (Yes/No only): 3900
  - Number of 'yes': 1932
  - Number of 'no':  1968
  - Percent 'no':    50.46%
Other or missing values (not counted in percent): 0
Interpretation: Majority answered 'No'.
```

---
