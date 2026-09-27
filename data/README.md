# Data dictionary

## gms_scores.csv

One row per included study (n = 35). Governance Maturity Score totals and model-class
assignments are reproduced from Supplementary Tables S7 and S8 of the article, where
the dimension-level evidence supporting every score is provided in full.

| Column | Type | Description |
|---|---|---|
| `study_id` | integer, 1–35 | Study identifier used throughout the article and supplementary tables |
| `system_group` | string | Name of the conversational agent where a system was evaluated in more than one study (Parentbot, Woebot, ALBA, Rover); blank where the system appears once; used in sensitivity analysis 1 |
| `gms_total` | integer, 0–24 | Governance Maturity Score, the sum of six anchored dimension scores (privacy, safety, monitoring, regulation, bias and fairness, consent), each scored 0–4 |
| `model_class_analytic` | string | Model class after applying the response-generation rule described in the article Methods |
| `model_class_raw` | string | Model class as originally extracted, before the response-generation rule was applied; used in sensitivity analysis 3 |
| `publication_year` | integer | Year of publication; used in sensitivity analysis 2 |

Model classes are Rule-based, Classical ML, Hybrid, LLM, Unspecified AI and Not reported.
The five studies classified as unspecified AI or not reported cannot be ordered by
architecture and are excluded from all inferential comparisons (30 of 35 studies;
25 of 30 unique systems).

Band labels used descriptively in the article: None 0–3, Basic 4–7, Moderate 8–11,
Advanced 12–14, Comprehensive 15–24. All inferential analyses use the continuous total.

## governance_elements.csv

One row per included study (n = 35), keyed by `study_id`. Each remaining column records
whether a specific governance element was reported (1) or not reported (0):
`explicit_consent`, `named_regulation`, `privacy_at_rest`, `storage_location`,
`clinical_supervision`, `human_crisis_pathway`, `automated_detection`, `ai_identity`,
`bias_fairness`.

## Sensitivity analyses

All four are run by `analysis/analysis_script.py`, comparing rule-based systems with
LLM and hybrid systems:

1. **Unique systems.** Studies of the same system (`system_group`) are collapsed to their mean score, so each system counts once.
2. **2022–2025 cohort.** Restricted to studies published 2022–2025 (`publication_year`).
3. **Raw extracted classes.** Uses `model_class_raw` in place of `model_class_analytic`.
4. **Journal publications only.** Restricted to peer-reviewed journal articles. The study IDs are listed in `JOURNAL_IDS` in the analysis script.
