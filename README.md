# Governance and privacy in AI-supported conversational agents for perinatal mental health

Analysis code and data for the scoping review *A scoping review of governance and privacy in AI-supported conversational agents for perinatal mental health*.

This repository reproduces every inferential statistic reported in the article, and generates the published figures.

---

## Reproduce the analysis

```bash
git clone https://github.com/DesmondObe/perinatal-CA-governance-review.git
cd perinatal-CA-governance-review
pip install -r requirements.txt
python analysis/analysis_script.py
```

Runs in under a second. The expected output is stored in [`outputs/analysis_output.txt`](outputs/analysis_output.txt); the script prints the manuscript's reported values alongside the computed ones so any discrepancy is immediately visible.

---

## What is here

```
├── data/
│   ├── gms_scores.csv          Governance Maturity Score totals and model classes (n = 34)
│   └── README.md               Data dictionary
├── analysis/
│   └── analysis_script.py      All inferential statistics
├── figures/
│   └── figures.ipynb           Figures 2, 3 and 4
├── outputs/
│   └── analysis_output.txt     Captured output of a verified run
├── requirements.txt
├── CITATION.cff
└── LICENSE                     CC BY 4.0
```

---

## What the analysis does

The review scored governance across six dimensions (privacy, safety, monitoring, regulation, bias and fairness, consent), each anchored 0–4 and summed to a Governance Maturity Score of 0–24 per study. `analysis_script.py` tests whether that score differs by conversational model class.

| Analysis | Test | Reported result |
|---|---|---|
| Omnibus, four defined model classes (n = 29 studies) | Kruskal–Wallis | H = 11.55, p = 0.009 |
| **Primary contrast**, rule-based vs LLM-and-hybrid | Mann–Whitney U | U = 152.0, p = 0.003, r = 0.67 |
| Secondary, ordinal complexity vs governance | Spearman | rho = −0.53, p = 0.003 |
| Sensitivity 1, unique systems (n = 25) | Kruskal–Wallis, Mann–Whitney | H = 9.83, p = 0.020; U = 109.0, p = 0.007 |
| Sensitivity 2, studies published 2022–2025 | Mann–Whitney U | medians 11.0 vs 6.0; U = 112.0, p = 0.005 |
| Sensitivity 3, raw extracted model classes | Mann–Whitney U | medians 11.0 vs 6.0; U = 131.5, p = 0.011, r = 0.59 |

Given tied observations, Mann–Whitney p values use the asymptotic normal approximation with tie correction, and Kruskal–Wallis p values the asymptotic chi-squared reference distribution. Because the Governance Maturity Score and these comparisons were developed after protocol registration, they are exploratory and support rather than establish the observed patterns.

The five studies classified as unspecified AI or not reported cannot be ordered by architecture and are excluded from all inferential comparisons.

---

## Figures

`figures/figures.ipynb` generates four of the five figures in the article. Figure 1, the PRISMA-ScR flow diagram, is produced separately.

| Notebook cell | Figure | Content | Output files |
|---|---|---|---|
| 3 | **Fig. 2** | Geographic distribution of perinatal conversational agent development, 30 unique systems coloured by World Bank income group | `fig_geography.png`, `fig_geography.pdf` |
| 5 | **Fig. 3** | Publications over time by model class, 34 studies, stacked bars across non-overlapping periods | `fig_pubtime.png`, `fig_pubtime.pdf` |
| 6 | **Fig. 4** | Governance Maturity Profile, mean score per dimension (0-4) across 34 studies | `fig_radar_corrected.png`, `fig_radar_corrected.pdf` |
| 7 | **Fig. 5** | Governance maturity by model class and crisis-escalation tier, each study plotted by class against its total score | `fig_governance_by_class.png` |

Open in Jupyter and run all cells. All figures are written at 300 dpi; `geopandas` is required for the map in cell 3.

---

## Data provenance

`data/gms_scores.csv` is derived from the verified extraction dataset described in the article. Every score traces to dimension-level evidence quoted from the source publication, provided in full in Supplementary Table S8. The complete extraction dataset, correction log and variable codebook accompany the article as Supplementary Data and are deposited on the Open Science Framework.

Review protocol: [osf.io/63mpb](https://osf.io/63mpb) (registered 3 November 2025)

---

## Citing this work

Please cite the article, and the software if you use or adapt the code:

> Full article citation would be added on acceptance]

> Zenodo DOI will be added when created

GitHub renders a "Cite this repository" button from [`CITATION.cff`](CITATION.cff).

---

## Licence

[CC BY 4.0](LICENSE). Reuse and adaptation are permitted with attribution.
