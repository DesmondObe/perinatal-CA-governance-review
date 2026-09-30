# Data dictionary

Both files have one row per included study (N = 35), keyed by `study_id`. They are derived from Supplementary Data 1 of the article.

## gms_scores.csv

| Column | Type | Description |
|---|---|---|
| `study_id` | integer, 1–35 | Study identifier used throughout the article and Supplementary Data 1 |
| `system_group` | string | System name where a system was evaluated in more than one study (Parentbot, Woebot, ALBA, Rover); blank otherwise. Used in sensitivity 1 |
| `publication_year` | integer | Year of publication. Used in sensitivity 2 and Fig. 3 |
| `venue` | `Journal` or `Conference` | Publication type. Used in sensitivity 4 |
| `model_class_analytic` | string | Model class after applying the response-generation rule (Methods) |
| `model_class_raw` | string | Model class as originally extracted. Used in sensitivity 3 (see note below) |
| `crisis_tier` | string | Highest documented crisis-escalation tier (Table 3). Used in Fig. 5 |
| `privacy`, `safety`, `monitoring`, `regulation`, `bias_fairness`, `consent` | integer, 0–4 | GMS dimension scores. Used in Fig. 6 |
| `gms_total` | integer, 0–24 | Governance Maturity Score, the sum of the six dimension scores |

Model classes: Rule-based, Classical ML, Hybrid, LLM, Unspecified AI, Not reported.

Crisis tiers: Automated detection + human follow-up; Automated detection (no human); Human-in-the-loop; Hotline / emergency contacts; Static disclaimer only; None; Not reported. Note that `None` is a category (no escalation mechanism), not missing data; read the file with `keep_default_na=False` in pandas.

**Raw classes.** `model_class_raw` maps the extracted labels in Supplementary Data 1 (sheet 1) to the six classes: "Hybrid (RAG-LLM + ML)" and "Rule-based + Classical ML" are coded Hybrid, "LLM (RAG)" is coded LLM, and Study 3's "Not reported" is coded Unspecified AI (commercial voice assistants). Only the Hybrid and LLM codings affect sensitivity 3.

GMS bands used descriptively in the article: None 0–3, Basic 4–7, Moderate 8–11, Advanced 12–14, Comprehensive 15–24. All inferential analyses use the continuous total.

## governance_elements.csv

Nine governance elements, coded 1 (reported) or 0 (not reported): `explicit_consent`, `named_regulation`, `privacy_at_rest`, `storage_location`, `clinical_supervision`, `human_crisis_pathway`, `automated_detection`, `ai_identity`, `bias_fairness`. These produce Fig. 7 and Supplementary Data 1, sheet 8. `ai_identity` counts partial disclosure (Fig. 7 footnote).
