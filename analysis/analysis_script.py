#!/usr/bin/env python3
"""
Statistical analyses for:

    Scoping review of governance, privacy, and design in AI-supported
    conversational agents for perinatal mental health.

Inputs
    data/gms_scores.csv           one row per included study (N = 35)
    data/governance_elements.csv  nine reported / not-reported governance
                                  elements per study (N = 35)

Output
    Printed to the console and written to outputs/analysis_output.txt,
    ending with a summary of the values reported in the article.

Usage
    python analysis/analysis_script.py
"""
import csv
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
GMS_FILE = ROOT / "data" / "gms_scores.csv"
ELEMENTS_FILE = ROOT / "data" / "governance_elements.csv"
OUTPUT_FILE = ROOT / "outputs" / "analysis_output.txt"

DEFINED = ("Rule-based", "Classical ML", "Hybrid", "LLM")
ALL_CLASSES = DEFINED + ("Unspecified AI", "Not reported")
DIMENSIONS = ("privacy", "safety", "monitoring", "regulation",
              "bias_fairness", "consent")
# Ordinal architectural complexity, used only for the secondary Spearman test
COMPLEXITY_RANK = {"Rule-based": 1, "Classical ML": 2, "Hybrid": 3, "LLM": 4}



# ------------------------------------------------------------------ helpers
class Tee:
    """Write to the console and to a file at the same time."""

    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(path, "w", encoding="utf-8")

    def __call__(self, text=""):
        print(text)
        self.file.write(text + "\n")

    def close(self):
        self.file.close()


def load_studies():
    with open(GMS_FILE, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    studies = {}
    for r in rows:
        sid = int(r["study_id"])
        dims = {d: int(r[d]) for d in DIMENSIONS}
        total = int(r["gms_total"])
        if sum(dims.values()) != total:
            raise ValueError(f"Study {sid}: dimension scores do not sum to gms_total")
        for col in ("model_class_analytic", "model_class_raw"):
            if r[col] not in ALL_CLASSES:
                raise ValueError(f"Study {sid}: unknown {col} '{r[col]}'")
        if r["venue"] not in ("Journal", "Conference"):
            raise ValueError(f"Study {sid}: unknown venue '{r['venue']}'")
        studies[sid] = {
            "total": total,
            "cls": r["model_class_analytic"],
            "raw": r["model_class_raw"],
            "year": int(r["publication_year"]),
            "venue": r["venue"],
            "system": r["system_group"].strip() or f"study_{sid}",
        }
    if sorted(studies) != list(range(1, 36)):
        raise ValueError("Expected study IDs 1 to 35")
    return studies


def load_elements():
    with open(ELEMENTS_FILE, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {int(r["study_id"]): {k: int(v) for k, v in r.items() if k != "study_id"}
            for r in rows}


def scores(studies, classes, key="cls", keep=lambda s: True):
    return [s["total"] for _, s in sorted(studies.items())
            if s[key] in classes and keep(s)]


def rank_biserial(a, b, u):
    """Rank-biserial correlation; positive when `a` tends to score higher."""
    return 2 * u / (len(a) * len(b)) - 1


def band(total):
    for upper, name in ((3, "None"), (7, "Basic"), (11, "Moderate"), (14, "Advanced")):
        if total <= upper:
            return name
    return "Comprehensive"


def compare(out, label, a, b):
    """Two-sided Mann-Whitney U (asymptotic, tie-corrected) with effect size."""
    res = stats.mannwhitneyu(a, b, alternative="two-sided")
    r = rank_biserial(a, b, res.statistic)
    out(f"{label}: rule-based n={len(a)}, median {np.median(a):.1f} vs "
        f"LLM + hybrid n={len(b)}, median {np.median(b):.1f}; "
        f"U={res.statistic:.1f}, p={res.pvalue:.4f}, r={r:.2f}")
    return res.statistic, res.pvalue, r


# ----------------------------------------------------------------- analyses
def main():
    studies = load_studies()
    elements = load_elements()
    out = Tee(OUTPUT_FILE)
    results = {}

    # Descriptive
    allv = [s["total"] for s in studies.values()]
    q1, q3 = np.percentile(allv, [25, 75])
    out("=== Descriptive (N = 35 studies) ===")
    out(f"mean {np.mean(allv):.2f}, median {np.median(allv):.1f}, "
        f"IQR {q1:.1f}-{q3:.1f}, range {min(allv)}-{max(allv)}")
    bands = [band(v) for v in allv]
    out("bands: " + "; ".join(
        f"{b} {bands.count(b)} ({100 * bands.count(b) / len(allv):.0f}%)"
        for b in ("None", "Basic", "Moderate", "Advanced", "Comprehensive")))
    results["median"] = np.median(allv)
    for c in DEFINED + ("LLM + hybrid",):
        v = scores(studies, ("Hybrid", "LLM") if c == "LLM + hybrid" else (c,))
        a, b = np.percentile(v, [25, 75])
        out(f"  {c:13} n={len(v):2d}  median {np.median(v):4.1f}  "
            f"IQR {a:.1f}-{b:.1f}  range {min(v)}-{max(v)}")

    # Element-level reporting (Fig. 7)
    out("\n=== Governance elements reported, by model class (Fig. 7) ===")
    groups = ("Rule-based", "Hybrid", "LLM", "Classical ML")
    out(f"{'element':24}" + "".join(f"{g:>16}" for g in groups))
    for e in next(iter(elements.values())):
        line = f"{e:24}"
        for g in groups:
            ids = [i for i, s in studies.items() if s["cls"] == g]
            k = sum(elements[i][e] for i in ids)
            line += f"{k:>9}/{len(ids):<2}{100 * k / len(ids):>4.0f}%"
        out(line)

    # Primary analysis
    out("\n=== Primary analysis (studies in the four defined classes, n = 30) ===")
    rb, ml, hy, llm = (scores(studies, (c,)) for c in DEFINED)
    h, p = stats.kruskal(rb, ml, hy, llm)
    out(f"Kruskal-Wallis, four classes: H={h:.2f}, p={p:.4f}")
    h3, p3 = stats.kruskal(rb, hy, llm)
    out(f"Kruskal-Wallis, three classes (excluding classical ML, n={len(rb + hy + llm)}): "
        f"H={h3:.2f}, p={p3:.4f}")
    u, results["p"], r = compare(out, "Mann-Whitney U", rb, hy + llm)
    ids = [i for i, s in studies.items() if s["cls"] in COMPLEXITY_RANK]
    rho, p_rho = stats.spearmanr([COMPLEXITY_RANK[studies[i]["cls"]] for i in ids],
                                 [studies[i]["total"] for i in ids])
    out(f"Spearman, complexity rank (rule-based < classical ML < hybrid < LLM) vs GMS: "
        f"rho={rho:.2f}, p={p_rho:.4f} [not reported in the article; the relationship "
        f"is not monotonic]")

    # Sensitivity 1: one value per system
    out("\n=== Sensitivity 1: multi-study systems collapsed to their mean ===")
    per_system = {}
    for s in studies.values():
        if s["cls"] in DEFINED:
            per_system.setdefault((s["system"], s["cls"]), []).append(s["total"])
    by_cls = {c: [float(np.mean(v)) for (_, k), v in per_system.items() if k == c]
              for c in DEFINED}
    h1, p1 = stats.kruskal(*by_cls.values())
    out(f"n={sum(len(v) for v in by_cls.values())} systems; "
        f"Kruskal-Wallis H={h1:.2f}, p={p1:.4f}")
    u1, results["p1"], _ = compare(out, "Mann-Whitney U", by_cls["Rule-based"],
                               by_cls["Hybrid"] + by_cls["LLM"])

    # Sensitivity 2: 2022-2025 publications
    out("\n=== Sensitivity 2: studies published 2022-2025 ===")
    recent = lambda s: s["year"] >= 2022
    u2, results["p2"], _ = compare(out, "Mann-Whitney U",
                       scores(studies, ("Rule-based",), keep=recent),
                       scores(studies, ("Hybrid", "LLM"), keep=recent))

    # Sensitivity 3: raw extracted classes
    out("\n=== Sensitivity 3: raw extracted classes (response-generation rule not applied) ===")
    u3, results["p3"], r3 = compare(out, "Mann-Whitney U",
                        scores(studies, ("Rule-based",), key="raw"),
                        scores(studies, ("Hybrid", "LLM"), key="raw"))

    # Sensitivity 4: journal publications only
    out("\n=== Sensitivity 4: peer-reviewed journal publications only ===")
    journal = lambda s: s["venue"] == "Journal"
    u4, results["p4"], r4 = compare(out, "Mann-Whitney U",
                        scores(studies, ("Rule-based",), keep=journal),
                        scores(studies, ("Hybrid", "LLM"), keep=journal))

    # Summary of values reported in the article
    fmt_p = lambda p: f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"
    out("\n=== Summary for the article ===")
    out(f"GMS, all studies: median {results['median']:.0f} (IQR {q1:g}-{q3:g}), "
        f"mean {np.mean(allv):.1f}, range {min(allv)}-{max(allv)}")
    out(f"Kruskal-Wallis, four classes: H = {h:.2f}, {fmt_p(p)}")
    out(f"Primary: rule-based median {np.median(rb):g} vs LLM + hybrid median "
        f"{np.median(hy + llm):g}; U = {u:.1f}, {fmt_p(results['p'])}, r = {r:.2f}")
    out(f"Sensitivity 1: H = {h1:.2f}, {fmt_p(p1)}; U = {u1:.1f}, {fmt_p(results['p1'])}")
    out(f"Sensitivity 2: U = {u2:.1f}, {fmt_p(results['p2'])}")
    out(f"Sensitivity 3: U = {u3:.1f}, {fmt_p(results['p3'])}, r = {r3:.2f}")
    out(f"Sensitivity 4: U = {u4:.1f}, {fmt_p(results['p4'])}, r = {r4:.2f}")
    out(f"\nPython {sys.version.split()[0]}, numpy {np.__version__}, scipy {scipy.__version__}")
    out.close()


if __name__ == "__main__":
    main()