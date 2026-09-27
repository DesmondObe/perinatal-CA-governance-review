#!/usr/bin/env python3
"""
Analyses for:

    A scoping review of governance and privacy in AI-supported conversational
    agents for perinatal mental health.

 
Input:  data/gms_scores.csv            GMS totals and model-class assignments
                                       for the 35 included studies
                                       (Supplementary Tables S7 and S8 hold
                                       the underlying dimension-level evidence)
        data/governance_elements.csv   optional; per-study presence or absence
                                       of the nine charted governance elements.
                                       If absent, that section is skipped.
Usage:  python analysis/analysis_script.py > outputs/analysis_output.txt
Requires: numpy, scipy (see requirements.txt)
"""
import csv
import os
import numpy as np
import scipy
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "gms_scores.csv")
ELEM = os.path.join(HERE, "..", "data", "governance_elements.csv")

# ---------------------------------------------------------------- load data
with open(DATA, newline="") as fh:
    rows = list(csv.DictReader(fh))

T = {int(r["study_id"]): int(r["gms_total"]) for r in rows}
CLASS = {int(r["study_id"]): r["model_class_analytic"].strip() for r in rows}
RAW = {int(r["study_id"]): r["model_class_raw"].strip() for r in rows}
YEAR = {int(r["study_id"]): int(r["publication_year"]) for r in rows}
SYSTEM = {int(r["study_id"]): r["system_group"].strip() for r in rows}

# Publication venue
JOURNAL_IDS = {
    1,2,3,4,5,8,11,12,14,16,17,18,19,20,22,23,
    26,27,28,29,30,31,34,35
}

# ---------------------------------------------------------- publication venue
# Peer-reviewed journal study IDs from the study-characteristics table.
# All remaining included studies are conference publications.

JOURNAL_IDS = {
    1, 2, 3, 4, 5, 8, 11, 12, 14, 16, 17, 18,
    19, 20, 22, 23, 26, 27, 28, 29, 30, 31, 34, 35
}

VENUE = {
    i: ("Journal" if i in JOURNAL_IDS else "Conference")
    for i in T
}


DEFINED = ("Rule-based", "Classical ML", "Hybrid", "LLM")
N = len(T)


def totals(cls, mapping=CLASS):
    return [T[i] for i in sorted(T) if mapping[i] == cls]


def rank_biserial(a, b, U):
    """Rank-biserial correlation for Mann-Whitney U.

    U is the statistic for sample `a` as returned by scipy. Positive values
    indicate that `a` tends to score higher than `b`. The sign is retained so
    that a reversal of direction would be visible rather than masked.
    """
    return 2 * U / (len(a) * len(b)) - 1


def band(t):
    if t <= 3:
        return "None"
    if t <= 7:
        return "Basic"
    if t <= 11:
        return "Moderate"
    if t <= 14:
        return "Advanced"
    return "Comprehensive"


# ------------------------------------------------------------- descriptives
allv = [T[i] for i in sorted(T)]
q1, q3 = np.percentile(allv, [25, 75])
print("=== Descriptive ===")
print(f"n={N}  mean={np.mean(allv):.2f}  median={np.median(allv):.1f}  "
      f"IQR={q1:.0f}-{q3:.1f}  range={min(allv)}-{max(allv)}")

counts = {}
for v in allv:
    counts[band(v)] = counts.get(band(v), 0) + 1
print("  bands: " + "; ".join(
    f"{b} {counts.get(b, 0)} ({100 * counts.get(b, 0) / N:.0f}%)"
    for b in ("None", "Basic", "Moderate", "Advanced", "Comprehensive")))

for c in DEFINED:
    v = totals(c)
    print(f"  {c:14} n={len(v):2d}  median={np.median(v):5.1f}  "
          f"range={min(v)}-{max(v)}")
lh_desc = totals("Hybrid") + totals("LLM")
print(f"  {'LLM + hybrid':14} n={len(lh_desc):2d}  "
      f"median={np.median(lh_desc):5.1f}  range={min(lh_desc)}-{max(lh_desc)}")

# ------------------------------------ element-level cross-tabulation (leads)
print("\n=== Element-level governance reporting by model class ===")
TRUEY = {"1", "yes", "y", "true", "t"}
if os.path.exists(ELEM):
    with open(ELEM, newline="") as fh:
        erows = list(csv.DictReader(fh))
    elements = [c for c in erows[0].keys() if c != "study_id"]
    grouped = {"Rule-based": [], "Hybrid": [], "LLM": []}
    for r in erows:
        sid = int(r["study_id"])
        cls = CLASS.get(sid, "")
        if cls in grouped:
            grouped[cls].append(r)
    print(f"{'element':34}" + "".join(f"{g:>18}" for g in grouped))
    for e in elements:
        line = f"{e:34}"
        for g, rs in grouped.items():
            k = sum(1 for r in rs if str(r[e]).strip().lower() in TRUEY)
            line += f"{k:>8}/{len(rs):<3}{100 * k / len(rs):>5.0f}%"
        print(line)
else:
    print("data/governance_elements.csv not found - section skipped.")
    print("To reproduce the paradox table, create it with columns:")
    print("  study_id, explicit_consent, named_regulation, privacy_at_rest,")
    print("  storage_location, clinical_supervision, human_crisis_pathway,")
    print("  automated_detection, ai_identity, bias_fairness")
    print("using 1 for reported and 0 for not reported.")

# ------------------------------------------- primary analysis (study level)
rb, ml, hy, llm = (totals(c) for c in DEFINED)
lh = hy + llm

print("\n=== Primary analysis: governance by model class (study level) ===")
H, p_kw = stats.kruskal(rb, ml, hy, llm)
print(f"Kruskal-Wallis, four defined classes (n={len(rb + ml + hy + llm)} studies): "
      f"H={H:.2f}, p={p_kw:.4f}")
H3, p_kw3 = stats.kruskal(rb, hy, llm)
print(f"Kruskal-Wallis, three classes excluding classical ML "
      f"(n={len(rb + hy + llm)} studies): H={H3:.2f}, p={p_kw3:.4f}")
res = stats.mannwhitneyu(rb, lh, alternative="two-sided")
print(f"Mann-Whitney U, rule-based (n={len(rb)}, median {np.median(rb):.1f}) "
      f"vs LLM+hybrid (n={len(lh)}, median {np.median(lh):.1f}): "
      f"U={res.statistic:.1f}, p={res.pvalue:.4f}, "
      f"rank-biserial r={rank_biserial(rb, lh, res.statistic):.2f}")

rank = {"Rule-based": 1, "Classical ML": 2, "Hybrid": 3, "LLM": 4}
xs = [rank[CLASS[i]] for i in sorted(T) if CLASS[i] in rank]
ys = [T[i] for i in sorted(T) if CLASS[i] in rank]
rho, p_sp = stats.spearmanr(xs, ys)
print(f"Spearman (secondary; relationship is not monotonic, so reported as "
      f"descriptive only): rho={rho:.2f}, p={p_sp:.4f}")

# -------------------------------------------- sensitivity 1: unique systems
print("\n=== Sensitivity 1: unique systems "
      "(multi-study systems collapsed to the mean) ===")
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
print(f"n={len(s_rb + s_ml + s_hy + s_llm)} systems | "
      f"Kruskal-Wallis H={H2:.2f}, p={p2:.4f}")
print(f"rule-based n={len(s_rb)} median={np.median(s_rb):.1f} vs "
      f"LLM+hybrid n={len(s_lh)} median={np.median(s_lh):.1f}")
print(f"Mann-Whitney U={res2.statistic:.1f}, p={res2.pvalue:.4f}, "
      f"rank-biserial r={rank_biserial(s_rb, s_lh, res2.statistic):.2f}")

# ------------------------------------------- sensitivity 2: 2022-2025 cohort
print("\n=== Sensitivity 2: studies published 2022-2025 ===")
rb3 = [T[i] for i in sorted(T) if CLASS[i] == "Rule-based" and YEAR[i] >= 2022]
lh3 = [T[i] for i in sorted(T) if CLASS[i] in ("Hybrid", "LLM") and YEAR[i] >= 2022]
res3 = stats.mannwhitneyu(rb3, lh3, alternative="two-sided")
print(f"rule-based n={len(rb3)} median={np.median(rb3):.1f} vs "
      f"LLM+hybrid n={len(lh3)} median={np.median(lh3):.1f}")
print(f"Mann-Whitney U={res3.statistic:.1f}, p={res3.pvalue:.4f}, "
      f"rank-biserial r={rank_biserial(rb3, lh3, res3.statistic):.2f}")

# ---------------------------------------- sensitivity 3: raw extracted classes
print("\n=== Sensitivity 3: raw extracted model classes "
      "(response-generation rule not applied) ===")
rb4 = totals("Rule-based", RAW)
lh4 = totals("Hybrid", RAW) + totals("LLM", RAW)
res4 = stats.mannwhitneyu(rb4, lh4, alternative="two-sided")
print(f"rule-based n={len(rb4)} median={np.median(rb4):.1f} vs "
      f"LLM+hybrid n={len(lh4)} median={np.median(lh4):.1f}")
print(f"Mann-Whitney U={res4.statistic:.1f}, p={res4.pvalue:.4f}, "
      f"rank-biserial r={rank_biserial(rb4, lh4, res4.statistic):.2f}")


# -------------------------------- sensitivity 4: journal publications only
print("\n=== Sensitivity 4: journal publications only ===")

rb5_ids = [i for i in T if i in JOURNAL_IDS and CLASS[i] == "Rule-based"]
lh5_ids = [i for i in T if i in JOURNAL_IDS and CLASS[i] in ("Hybrid", "LLM")]

rb5 = [T[i] for i in rb5_ids]
lh5 = [T[i] for i in lh5_ids]

res5 = stats.mannwhitneyu(rb5, lh5, alternative="two-sided")
r5 = rank_biserial(rb5, lh5, res5.statistic)

print(f"rule-based n={len(rb5)} median={np.median(rb5):.1f} vs "
      f"LLM+hybrid n={len(lh5)} median={np.median(lh5):.1f}")

print(f"U={res5.statistic:.1f}, p={res5.pvalue:.4f}, r={r5:.2f}")

print(f"Rule-based studies: {rb5_ids}")
print(f"LLM+hybrid studies: {lh5_ids}")



# ------------------------------------------------------------------ summary
print("\n=== Values to report in the manuscript (N = 35 studies) ===")
print(f"Primary       : H={H:.2f} p={p_kw:.3f} "
      f"(n={len(rb + ml + hy + llm)} studies in four defined classes)")
print(f"                U={res.statistic:.1f} p={res.pvalue:.3f} "
      f"r={rank_biserial(rb, lh, res.statistic):.2f}; "
      f"medians rule-based {np.median(rb):.1f} vs LLM+hybrid {np.median(lh):.1f}")
print(f"Spearman      : rho={rho:.2f} p={p_sp:.3f} (secondary, descriptive only)")
print(f"Sensitivity 1 : n={len(s_rb + s_ml + s_hy + s_llm)} systems; "
      f"H={H2:.2f} p={p2:.3f}; U={res2.statistic:.1f} p={res2.pvalue:.3f}; "
      f"medians {np.median(s_rb):.1f} vs {np.median(s_lh):.1f}")
print(f"Sensitivity 2 : medians {np.median(rb3):.1f} vs {np.median(lh3):.1f}; "
      f"U={res3.statistic:.1f} p={res3.pvalue:.3f} "
      f"(n={len(rb3)} vs {len(lh3)})")
print(f"Sensitivity 3 : medians {np.median(rb4):.1f} vs {np.median(lh4):.1f}; "
      f"U={res4.statistic:.1f} p={res4.pvalue:.3f} "
      f"r={rank_biserial(rb4, lh4, res4.statistic):.2f} "
      f"(n={len(rb4)} vs {len(lh4)})")
print(f"Sensitivity 4 : medians {np.median(rb5):.1f} vs {np.median(lh5):.1f}; "
      f"U={res5.statistic:.1f} p={res5.pvalue:.3f} "
      f"r={r5:.2f} "
      f"(n={len(rb5)} vs {len(lh5)})")
print(f"\nGenerated by analysis/analysis_script.py using "
      f"numpy {np.__version__}, scipy {scipy.__version__}")
