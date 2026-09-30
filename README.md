# Governance, privacy and design in AI-supported conversational agents for perinatal mental health

Analysis code and data for the article *Scoping review of governance, privacy, and design in AI-supported conversational agents for perinatal mental health* (Obe, Teague, Lee and Shatte).

The repository reproduces every inferential statistic reported in the article and regenerates Figs. 2 to 7.

## Reproduce the analysis

```bash
git clone https://github.com/DesmondObe/perinatal-CA-governance-review.git
cd perinatal-CA-governance-review
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python analysis/analysis_script.py
```

The script prints all results and writes them to `outputs/analysis_output.txt`, ending with a summary of the values reported in the article. The analyses in the article used Python 3.11, NumPy 1.26.4 and SciPy 1.11.4.

To regenerate the figures, open `figures/figures.ipynb` from the `figures/` folder and run all cells. Figures are written to `figures/output/` as PNG and PDF.

## Contents

```
├── data/
│   ├── gms_scores.csv            One row per study (N = 35): model class, venue, year,
│   │                             crisis-escalation tier, six GMS dimension scores and total
│   ├── governance_elements.csv   Nine governance elements, reported (1) or not (0), per study
│   └── README.md                 Data dictionary
├── analysis/
│   └── analysis_script.py        All descriptive and inferential statistics
├── figures/
│   ├── figures.ipynb             Figs. 2 to 7
│   ├── countries.geojson         Country boundaries for Fig. 2
│   └── output/                   Generated figures
├── outputs/
│   └── analysis_output.txt       Output of a verified run
├── requirements.txt
├── CITATION.cff
└── LICENSE                       MIT (code), CC BY 4.0 (data and figures)
```

## Analyses

Governance was scored on six dimensions (privacy, safety, monitoring, regulation, bias and fairness, consent), each anchored 0 to 4 and summed to a Governance Maturity Score (GMS) of 0 to 24 per study. The script tests whether the GMS differs by conversational model class.

| Analysis | Test | Result |
|---|---|---|
| Four defined model classes (n = 30 studies) | Kruskal–Wallis | H = 11.60, p = 0.009 |
| Primary contrast: rule-based vs LLM and hybrid | Mann–Whitney U | U = 161.5, p = 0.003, r = 0.66 |
| Sensitivity 1: one value per system (n = 25) | Kruskal–Wallis; Mann–Whitney U | H = 9.86, p = 0.020; U = 109.0, p = 0.007 |
| Sensitivity 2: studies published 2022–2025 | Mann–Whitney U | medians 11.0 vs 6.0; U = 119.5, p = 0.006 |
| Sensitivity 3: raw extracted model classes | Mann–Whitney U | medians 10.0 vs 6.0; U = 141.0, p = 0.013, r = 0.57 |
| Sensitivity 4: journal publications only | Mann–Whitney U | medians 10.5 vs 7.0; U = 79.5, p = 0.024, r = 0.62 |

Mann–Whitney p values use the asymptotic normal approximation with tie correction, and Kruskal–Wallis p values the asymptotic chi-squared distribution. r is the rank-biserial correlation. The five studies classified as unspecified AI or not reported cannot be ordered by architecture and are excluded from inferential comparisons. The GMS was developed after protocol registration, so these comparisons are exploratory.

The script also prints a Spearman correlation between an ordinal complexity rank and the GMS. It is not reported in the article because the relationship is not monotonic.

## Figures

| Article figure | Content | Source |
|---|---|---|
| Fig. 2 | Geographic distribution of the 30 unique systems | Counts entered in the notebook (Supplementary Data 1, sheet 1) |
| Fig. 3 | Publications over time by model class | `data/gms_scores.csv` |
| Fig. 4 | Clinical scope, functions and therapeutic foundations | Counts entered in the notebook (Supplementary Data 1, sheets 4 and 10) |
| Fig. 5 | GMS by model class and crisis-escalation tier | `data/gms_scores.csv` |
| Fig. 6 | Mean score on each GMS dimension | `data/gms_scores.csv` |
| Fig. 7 | Governance elements reported by model class | `data/governance_elements.csv` |

Fig. 1 (PRISMA-ScR flow diagram) is produced separately.

## Data provenance

The files in `data/` are derived from the verified extraction dataset, provided with the article as Supplementary Data 1. The evidence supporting every dimension score is in sheet 7 (GMS_Evidence), scores and totals in sheet 6 (GMS_Scores), and the full codebook and dataset in sheet 10. The review protocol and verified dataset are also on the Open Science Framework: https://osf.io/63mpb (registered 3 November 2025).

## Citation

Please cite the article, and this repository if you use or adapt the code. GitHub shows a "Cite this repository" button generated from `CITATION.cff`.

## Licence

Code is released under the MIT License. Data, figures and outputs are released under CC BY 4.0. See `LICENSE`.