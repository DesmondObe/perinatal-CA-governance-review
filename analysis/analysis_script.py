#!/usr/bin/env python3
"""
Inferential statistics for:

    A scoping review of governance and privacy in AI-supported conversational
    agents for perinatal mental health.

Reproduces every inferential statistic reported in the manuscript: the omnibus
comparison across model classes, the primary rule-based versus LLM-and-hybrid
contrast, the secondary Spearman correlation, and three sensitivity analyses.

Input:  data/gms_scores.csv  (Governance Maturity Score totals and model-class
        assignments for the 34 included studies; see Supplementary Tables S7
        and S8 for the underlying evidence)
Usage:  python analysis/analysis_script.py
Requires: numpy, scipy (see requirements.txt)
"""
import csv
import os
import numpy as np
from scipy import stats

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "gms_scores.csv")

# ---------------------------------------------------------------- load data
rows = list(csv.DictReader(open(DATA)))
T = {int(r["study_id"]): int(r["gms_total"]) for r in rows}
CLASS = {int(r["study_id"]): r["model_class_analytic"] for r in rows}
RAW = {int(r["study_id"]): r["model_class_raw"] for r in rows}
YEAR = {int(r["study_id"]): int(r["publication_year"]) for r in rows}
SYSTEM = {int(r["study_id"]): r["system_group"] for r in rows}

DEFINED = ("Rule-based", "Classical ML", "Hybrid", "LLM")


def totals(cls, mapping=CLASS):
    return [T[i] for i in sorted(T) if mapping[i] == cls]


def rank_biserial(a, b, U):
    return abs(1 - 2 * U / (len(a) * len(b)))


# ------------------------------------------------------------- descriptives
allv = [T[i] for i in sorted(T)]
q1, q3 = np.percentile(allv, [25, 75])
print("=== Descriptive ===")
print(f"n={len(allv)}  mean={np.mean(allv):.2f}  median={np.median(allv):.1f}  "
      f"IQR={q1:.0f}-{q3:.1f}  range={min(allv)}-{max(allv)}")
for c in DEFINED:
    v = totals(c)
    print(f"  {c:14} n={len(v):2d}  median={np.median(v):.1f}")

# ------------------------------------------------- primary analysis (study level)
rb, ml, hy, llm = (totals(c) for c in DEFINED)
lh = hy + llm

print("\n=== Primary analysis: governance by model class (study level) ===")
H, p_kw = stats.kruskal(rb, ml, hy, llm)
print(f"Kruskal-Wallis, four defined classes (n={len(rb+ml+hy+llm)} studies): "
      f"H={H:.2f}, p={p_kw:.4f}")
res = stats.mannwhitneyu(rb, lh, alternative="two-sided")
print(f"Mann-Whitney U, rule-based vs LLM+hybrid: U={res.statistic:.1f}, "
      f"p={res.pvalue:.4f}, rank-biserial r={rank_biserial(rb, lh, res.statistic):.2f}")

rank = {"Rule-based": 1, "Classical ML": 2, "Hybrid": 3, "LLM": 4}
xs = [rank[CLASS[i]] for i in sorted(T) if CLASS[i] in rank]
ys = [T[i] for i in sorted(T) if CLASS[i] in rank]
rho, p_sp = stats.spearmanr(xs, ys)
print(f"Spearman (secondary, relationship not monotonic): rho={rho:.2f}, p={p_sp:.4f}")

# --------------------------------------------- sensitivity 1: unique systems
print("\n=== Sensitivity 1: unique systems (multi-study systems collapsed to the mean) ===")
groups = {}
for i in sorted(T):
    key = SYSTEM[i] or f"study_{i}"
    groups.setdefault((key, CLASS[i]), []).append(T[i])
sys_by_class = {c: [] for c in DEFINED}
for (name, cls), vals in groups.items():
    if cls in DEFINED:
        sys_by_class[cls].append(float(np.mean(vals)))
s_rb, s_ml, s_hy, s_llm = (sys_by_class[c] for c in DEFINED)
s_lh = s_hy + s_llm
H2, p2 = stats.kruskal(s_rb, s_ml, s_hy, s_llm)
res2 = stats.mannwhitneyu(s_rb, s_lh, alternative="two-sided")
print(f"n={len(s_rb+s_ml+s_hy+s_llm)} systems | Kruskal-Wallis H={H2:.2f}, p={p2:.4f}")
print(f"Mann-Whitney U={res2.statistic:.1f}, p={res2.pvalue:.4f}")

# ------------------------------------------ sensitivity 2: 2022-2025 cohort
print("\n=== Sensitivity 2: studies published 2022-2025 ===")
rb3 = [T[i] for i in sorted(T) if CLASS[i] == "Rule-based" and YEAR[i] >= 2022]
lh3 = [T[i] for i in sorted(T) if CLASS[i] in ("Hybrid", "LLM") and YEAR[i] >= 2022]
res3 = stats.mannwhitneyu(rb3, lh3, alternative="two-sided")
print(f"rule-based n={len(rb3)} median={np.median(rb3):.1f} vs "
      f"LLM+hybrid n={len(lh3)} median={np.median(lh3):.1f}")
print(f"Mann-Whitney U={res3.statistic:.1f}, p={res3.pvalue:.4f}")

# --------------------------------------- sensitivity 3: raw extracted classes
print("\n=== Sensitivity 3: raw extracted model classes (response-generation rule not applied) ===")
rb4 = totals("Rule-based", RAW)
lh4 = totals("Hybrid", RAW) + totals("LLM", RAW)
res4 = stats.mannwhitneyu(rb4, lh4, alternative="two-sided")
print(f"rule-based n={len(rb4)} median={np.median(rb4):.1f} vs "
      f"LLM+hybrid n={len(lh4)} median={np.median(lh4):.1f}")
print(f"Mann-Whitney U={res4.statistic:.1f}, p={res4.pvalue:.4f}, "
      f"rank-biserial r={rank_biserial(rb4, lh4, res4.statistic):.2f}")

print("\n--- Expected values as reported in the manuscript ---")
print("Primary       : H=11.55 p=0.009 | U=152.0 p=0.003 r=0.67 | rho=-0.53 p=0.003")
print("Sensitivity 1 : H=9.83  p=0.020 | U=109.0 p=0.007")
print("Sensitivity 2 : medians 11.0 vs 6.0 | U=112.0 p=0.005")
print("Sensitivity 3 : medians 11.0 vs 6.0 | U=131.5 p=0.011 r=0.59")
