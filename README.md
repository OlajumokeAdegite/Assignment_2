#!/usr/bin/env python3
"""
analyze_smoking_health.py

Analyze a real-world health dataset with smoking indicators.

Features:
- Robust CSV loading with validation and friendly errors
- Conditional execution (choose tasks via --task flag)
- Descriptive statistics and group comparisons (smokers vs non-smokers)
- Simple rule-based "risk flags" derived from vitals
- Matplotlib charts saved to disk (no specific colors/styles)
- Cleaned dataset export

Usage examples:
  python analyze_smoking_health.py --csv smoking_health_data_final.csv --task summary
  python analyze_smoking_health.py --csv smoking_health_data_final.csv --task risk --bp-threshold 130
  python analyze_smoking_health.py --csv smoking_health_data_final.csv --task visualize --outdir outputs

Author: Generated with the help of generative AI.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


REQUIRED_COLS = ["age", "sex", "current_smoker", "heart_rate", "blood_pressure", "cigs_per_day", "chol"]


def load_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV: {e}")
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found columns: {list(df.columns)}")
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    # Attempt to coerce numeric columns; leave 'sex' and 'current_smoker' as-is then normalize them
    numeric_cols = ["age", "heart_rate", "blood_pressure", "cigs_per_day", "chol"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Normalize binary/categorical columns
    # current_smoker: accept {1,0}, {"yes","no"}, {"true","false"}, {"Y","N"}
    def to_bool(x):
        if pd.isna(x):
            return np.nan
        if isinstance(x, (int, float)) and not pd.isna(x):
            if x == 1:
                return True
            if x == 0:
                return False
        s = str(x).strip().lower()
        if s in {"yes", "y", "true", "t", "1"}:
            return True
        if s in {"no", "n", "false", "f", "0"}:
            return False
        return np.nan
    df["current_smoker"] = df["current_smoker"].apply(to_bool)

    # Normalize 'sex' to {'F','M'} when possible
    def norm_sex(x):
        if pd.isna(x): return np.nan
        s = str(x).strip().lower()
        if s in {"f", "female", "0"}: return "F"
        if s in {"m", "male", "1"}: return "M"
        return np.nan
    df["sex"] = df["sex"].apply(norm_sex)
    return df


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    before = len(df)
    df = df.copy()
    df = coerce_types(df)
    # Drop rows missing key analysis fields
    key_cols = ["age", "current_smoker", "heart_rate", "blood_pressure", "chol"]
    df_clean = df.dropna(subset=key_cols)
    after = len(df_clean)
    info = {
        "rows_before": before,
        "rows_after": after,
        "dropped": before - after,
        "na_counts": df.isna().sum().to_dict()
    }
    return df_clean, info


def describe_summary(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    overall = df[["age", "heart_rate", "blood_pressure", "cigs_per_day", "chol"]].describe().T
    by_smoke = df.groupby("current_smoker")[["age", "heart_rate", "blood_pressure", "chol", "cigs_per_day"]].agg(
        ["count", "mean", "std", "min", "max"]
    )
    by_sex_smoke = df.groupby(["sex", "current_smoker"])[["heart_rate", "blood_pressure", "chol"]].mean()
    return {"overall": overall, "by_smoker": by_smoke, "by_sex_smoker_mean": by_sex_smoke}


def risk_flags(df: pd.DataFrame, bp_threshold: float, hr_threshold: float, chol_threshold: float) -> pd.DataFrame:
    df = df.copy()
    # Simple rule-based flags (for demo): if any vital exceeds threshold, flag = 1 else 0
    df["flag_high_bp"] = (df["blood_pressure"] >= bp_threshold).astype(int)
    df["flag_high_hr"] = (df["heart_rate"] >= hr_threshold).astype(int)
    df["flag_high_chol"] = (df["chol"] >= chol_threshold).astype(int)
    # Combined risk score
    df["risk_score"] = df[["flag_high_bp", "flag_high_hr", "flag_high_chol"]].sum(axis=1)
    return df


def save_tables(tables: Dict[str, pd.DataFrame], outdir: Path) -> Dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, table in tables.items():
        p = outdir / f"{name}.csv"
        table.to_csv(p)
        paths[name] = p
    return paths


def plot_group_bars(df: pd.DataFrame, outdir: Path) -> List[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    plots = []

    # Mean vitals by smoking status
    means = df.groupby("current_smoker")[["heart_rate", "blood_pressure", "chol"]].mean()
    ax = means.plot(kind="bar")
    ax.set_title("Mean vitals by smoking status")
    ax.set_xlabel("current_smoker (False/True)")
    ax.set_ylabel("Mean value")
    fig = ax.get_figure()
    p1 = outdir / "mean_vitals_by_smoking.png"
    fig.tight_layout()
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    plots.append(p1)

    # Distribution of cigarettes per day for smokers
    smokers = df[df["current_smoker"] == True]
    if not smokers.empty:
        fig, ax = plt.subplots()
        smokers["cigs_per_day"].dropna().plot(kind="hist", bins=20, ax=ax)
        ax.set_title("Distribution of cigarettes per day (smokers only)")
        ax.set_xlabel("cigs_per_day")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        p2 = outdir / "cigs_per_day_hist.png"
        fig.savefig(p2, dpi=150)
        plt.close(fig)
        plots.append(p2)

    # Risk score distribution (if exists)
    if "risk_score" in df.columns:
        fig, ax = plt.subplots()
        df["risk_score"].plot(kind="hist", bins=4, ax=ax)
        ax.set_title("Risk score distribution (0-3)")
        ax.set_xlabel("risk_score")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        p3 = outdir / "risk_score_hist.png"
        fig.savefig(p3, dpi=150)
        plt.close(fig)
        plots.append(p3)

    return plots


def do_summary(df: pd.DataFrame, outdir: Path) -> None:
    tables = describe_summary(df)
    paths = save_tables(tables, outdir / "tables")
    print("Saved summary tables:")
    for name, p in paths.items():
        print(f"  - {name}: {p}")


def do_risk(df: pd.DataFrame, outdir: Path, bp_th: float, hr_th: float, chol_th: float) -> None:
    df_risk = risk_flags(df, bp_th, hr_th, chol_th)
    # Group comparison: mean risk_score by smoking
    grp = df_risk.groupby("current_smoker")["risk_score"].mean()
    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / "risk_flags.csv"
    df_risk.to_csv(out_csv, index=False)
    print(f"Risk flags and scores saved to: {out_csv}")
    print("\nMean risk_score by smoking status:")
    print(grp.to_string())
    plot_paths = plot_group_bars(df_risk, outdir / "plots")
    for p in plot_paths:
        print(f"Saved plot: {p}")


def do_visualize(df: pd.DataFrame, outdir: Path) -> None:
    plot_paths = plot_group_bars(df, outdir / "plots")
    print("Saved plots:")
    for p in plot_paths:
        print(f"  - {p}")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Analyze smoking & health dataset")
    parser.add_argument("--csv", required=True, help="Path to dataset CSV")
    parser.add_argument("--task", choices=["summary", "risk", "visualize"], default="summary",
                        help="Which task to run")
    parser.add_argument("--outdir", default="outputs", help="Directory to write outputs")
    parser.add_argument("--bp-threshold", type=float, default=130.0, help="Systolic BP threshold for risk flag")
    parser.add_argument("--hr-threshold", type=float, default=100.0, help="Heart rate threshold for risk flag")
    parser.add_argument("--chol-threshold", type=float, default=200.0, help="Cholesterol threshold for risk flag")

    args = parser.parse_args(argv)

    outdir = Path(args.outdir)
    csv_path = Path(args.csv)

    try:
        df_raw = load_csv(csv_path)
        df_clean, info = clean_data(df_raw)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    # Export cleaned dataset
    outdir.mkdir(parents=True, exist_ok=True)
    cleaned_csv = outdir / "cleaned_dataset.csv"
    df_clean.to_csv(cleaned_csv, index=False)

    print("=== Data Cleaning Report ===")
    for k, v in info.items():
        print(f"{k}: {v}")
    print(f"Cleaned dataset saved to: {cleaned_csv}\n")

    # Conditional execution of tasks
    if args.task == "summary":
        do_summary(df_clean, outdir)
    elif args.task == "risk":
        do_risk(df_clean, outdir, args.bp_threshold, args.hr_threshold, args.chol_threshold)
    elif args.task == "visualize":
        do_visualize(df_clean, outdir)
    else:
        print(f"Unknown task: {args.task}", file=sys.stderr)
        return 2

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
