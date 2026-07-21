# Data dictionary

## gms_scores.csv

One row per included study (n = 34). Governance Maturity Score totals and model-class
assignments are reproduced from Supplementary Tables S7 and S8 of the article, where
the dimension-level evidence supporting every score is provided in full.

| Column | Type | Description |
|---|---|---|
| `study_id` | integer, 1–34 | Study identifier used throughout the article and supplementary tables |
| `system_group` | string | Name of the conversational agent where a system was evaluated in more than one study (Parentbot, Woebot, ALBA); blank where the system appears once |
| `gms_total` | integer, 0–24 | Governance Maturity Score, the sum of six anchored dimension scores (privacy, safety, monitoring, regulation, bias and fairness, consent), each scored 0–4 |
| `model_class_analytic` | string | Model class after applying the response-generation rule described in the article Methods |
| `model_class_raw` | string | Model class as originally extracted, before the response-generation rule was applied; used in sensitivity analysis 3 |
| `publication_year` | integer | Year of publication; used in sensitivity analysis 2 |

Model classes are Rule-based, Classical ML, Hybrid, LLM, Unspecified AI and Not reported.
The five studies classified as unspecified AI or not reported cannot be ordered by
architecture and are excluded from all inferential comparisons (29 of 34 studies;
25 of 30 unique systems).

Band labels used descriptively in the article: None 0–3, Basic 4–7, Moderate 8–11,
Advanced 12–14, Comprehensive 15–24. All inferential analyses use the continuous total.
