#!/usr/bin/env python3
"""
Analyze a yes/no column in a CSV dataset.

Default behavior:
- Prints count of "Yes"
- Prints percent of "No"

You can change the column name and the labels via CLI args.

Examples:
  python analyze_smoking.py --csv data.csv --col "current_smoker"
  python analyze_smoking.py --csv data.csv --col "smoker_now" --yes "Y" --no "N"

Demonstrates conditional execution with clear if/elif/else branches.
"""

import argparse
import csv
import sys

def percent(part, whole):
    """Return 0–100 percentage; avoids division by zero."""
    return (part / whole * 100.0) if whole else 0.0

def main():
    parser = argparse.ArgumentParser(
        description="Analyze a yes/no column in a CSV file."
    )
    parser.add_argument("--csv", required=True, help="Path to the CSV file.")
    parser.add_argument("--col", required=True, help="Name of the yes/no column to analyze.")
    parser.add_argument("--yes", default="Yes", help='Label used for "yes" (default: Yes)')
    parser.add_argument("--no",  default="No",  help='Label used for "no"  (default: No)')
    parser.add_argument(
        "--case_insensitive",
        action="store_true",
        help="Treat labels case-insensitively."
    )
    args = parser.parse_args()

    try:
        with open(args.csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            # Conditional: verify the column exists
            if args.col not in headers:
                print(f"ERROR: Column '{args.col}' not found. Available columns: {headers}")
                sys.exit(1)

            total_valid = 0
            yes_count = 0
            no_count = 0
            missing_or_other = 0

            # Normalizer based on case handling
            def norm(x):
                if x is None:
                    return None
                s = str(x).strip()
                return s.lower() if args.case_insensitive else s

            yes_label = norm(args.yes)
            no_label  = norm(args.no)

            for row in reader:
                raw = row.get(args.col, None)
                if raw is None or str(raw).strip() == "":
                    missing_or_other += 1
                    continue

                val = norm(raw)

                # Conditional branches
                if val == yes_label:
                    yes_count += 1
                    total_valid += 1
                elif val == no_label:
                    no_count += 1
                    total_valid += 1
                else:
                    # Anything not exactly the yes/no labels counts as other
                    missing_or_other += 1

            # Conditional: avoid division by zero
            if (total_valid + missing_or_other) == 0:
                print("No rows to analyze.")
                sys.exit(0)

            no_percent = percent(no_count, total_valid)

            print("=== Analysis ===")
            print(f"CSV file: {args.csv}")
            print(f"Column analyzed: {args.col}")
            print(f"YES label: '{args.yes}', NO label: '{args.no}'")
            print(f"Valid responses (Yes/No only): {total_valid}")
            print(f"  - Number of '{args.yes}': {yes_count}")
            print(f"  - Number of '{args.no}':  {no_count}")
            print(f"  - Percent '{args.no}':    {no_percent:.2f}%")
            print(f"Other or missing values (not counted in percent): {missing_or_other}")

            # Extra conditional example: simple interpretation branch
            if no_percent > 50:
                print("Interpretation: Majority answered 'No'.")
            elif yes_count > no_count:
                print("Interpretation: More participants answered 'Yes' than 'No'.")
            else:
                print("Interpretation: Responses are roughly balanced or data is sparse.")

    except FileNotFoundError:
        print(f"ERROR: File not found: {args.csv}")
        sys.exit(1)
    except UnicodeDecodeError:
        print("ERROR: Could not decode the file. Try saving as UTF-8.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
