# Part 6 — Supervised AI Classifier Design Plan

## Purpose

Parts 1–5 convert raw or synthetic TESS light curves into a candidate-level catalog containing:

- detection features: period, duration, depth, SNR, SDE-like score, transit count
- refined transit parameters: fitted depth, duration, period, radius ratio proxy
- scientific vetting features: odd/even mismatch, secondary eclipse, centroid shift, crowding, shape, red-noise proxy, data quality
- transparent rule-based scores: planet, EB, blend, stellar variability, systematic

Part 6 uses the curated labeled dataset to learn a supervised classifier on top of those physically meaningful features.

The key design principle is:

> AI should classify candidate events from physically interpretable features, not blindly classify raw light curves before detection/vetting.

This keeps the pipeline explainable and makes the 3-page report easier to defend.

---

## Canonical classes

The classifier uses these project-level classes:

1. `PLANETARY_TRANSIT_CANDIDATE`
2. `ECLIPSING_BINARY`
3. `BLEND_OR_CONTAMINATED_SIGNAL`
4. `STELLAR_VARIABILITY`
5. `INSTRUMENTAL_OR_LOW_QUALITY_SYSTEMATIC`
6. `NO_SIGNIFICANT_SIGNAL`
7. `UNCERTAIN_TRANSIT_LIKE_SIGNAL`

The label-normalization layer maps organizer labels such as `planet`, `confirmed_planet`, `eb`, `background_eb`, `blend`, `starspot`, `false_positive`, and `noise` into these canonical classes. Unknown labels are not silently guessed.

---

## Why a tabular supervised classifier first?

A neural network on phase-folded light curves is possible later, but the first best-grade AI model should be tabular because:

- the curated dataset may be small or imbalanced;
- the features are physically meaningful;
- feature importance can be shown in the report;
- tabular models train quickly and are easy to validate;
- physical guardrails can be blended with the AI probabilities.

The implemented default model is a `RandomForestClassifier` with imputation and class balancing. It supports optional probability calibration when enough labeled examples exist per class.

---

## Feature groups

### Detection features

- `period_days`
- `duration_days`
- `depth_ppm`
- `snr`
- `local_snr`
- `sde`
- `n_transits`
- `n_full_transits`
- `n_in_transit_points`

### Refined fit features

- `fit_period_days`
- `fit_period_err_days`
- `fit_duration_days`
- `fit_duration_err_days`
- `fit_depth_ppm`
- `fit_depth_err_ppm`
- `fit_rp_over_rstar`
- `fit_event_depth_scatter_ppm`

### Vetting features

- `vet_odd_even_sigma`
- `vet_secondary_sigma`
- `vet_secondary_to_primary_ratio`
- `vet_centroid_shift_sigma`
- `vet_centroid_shift_pix`
- `vet_crowding_risk`
- `vet_crowdsap`
- `vet_corrected_depth_ppm`
- `vet_v_shape_score`
- `vet_red_noise_proxy`
- `vet_data_quality_score`

### Rule-based meta-features

- `class_planet_score`
- `class_eb_score`
- `class_blend_score`
- `class_stellar_variability_score`
- `class_systematic_score`

These are included as weak scientific priors. They are not labels. The model can learn when the rule-based baseline is helpful and when it is insufficient.

---

## Training flow

```text
labeled candidate catalog
    ↓
normalize labels
    ↓
select safe numeric features
    ↓
impute missing values
    ↓
stratified train/test split when possible
    ↓
train random forest / extra trees / histogram GBDT
    ↓
calibrate probabilities if enough examples exist
    ↓
evaluate accuracy, balanced accuracy, macro F1, confusion matrix
    ↓
save model bundle + model card + feature importances
```

---

## Prediction flow

```text
unlabeled Parts 1–5 candidate catalog
    ↓
AI class probabilities
    ↓
blend with rule-based scores
    ↓
apply physical guardrails
    ↓
final class probabilities + final label + confidence
```

Physical guardrails are applied for cases such as:

- strong secondary eclipse → push toward EB
- strong odd/even mismatch → push toward EB
- significant centroid shift → push toward blend
- low data quality → push toward systematic
- low SNR → push toward no-signal/uncertain

This prevents the AI model from calling an obvious EB or blend a high-confidence planet merely because of a learned statistical boundary.

---

## Deliverables added in Part 6

```text
src/exoplanet_pipeline/ml.py
src/exoplanet_pipeline/ml_synthetic.py
src/exoplanet_pipeline/ml_diagnostics.py
scripts/run_part6_synthetic_ai_demo.py
scripts/train_ai_classifier_from_catalog.py
scripts/predict_ai_classifier_catalog.py
tests/test_ml_part6.py
notebooks/06_part_6_ai_classifier_demo.ipynb
PART_6_AI_CLASSIFIER_DESIGN_PLAN.md
REPORT_DRAFT_PARTS_1_6.md
```

---

## How to use with the organizer's curated dataset

Assume the organizer gives a CSV with Parts 1–5-style features and a label column named `label`:

```bash
python scripts/train_ai_classifier_from_catalog.py curated_labeled_catalog.csv --label-col label --output-dir outputs_part6_ai
```

This writes:

```text
part6_ai_classifier.joblib
part6_ai_classifier_metrics.json
part6_ai_classifier_feature_importance.csv
part6_ai_classifier_MODEL_CARD.md
part6_confusion_matrix.png
part6_feature_importance.png
```

Then predict on unlabeled science candidates:

```bash
python scripts/predict_ai_classifier_catalog.py outputs_part6_ai/part6_ai_classifier.joblib candidate_catalog.csv --output-csv outputs_part6_ai/science_predictions.csv
```

---

## Evaluation metrics

The report should include:

- accuracy
- balanced accuracy
- macro F1
- class-wise precision/recall/F1
- confusion matrix
- top features
- examples of correct and incorrect classifications

Macro F1 is important because the dataset may be imbalanced. A model that only predicts the majority class can have misleadingly high accuracy.

---

## Important limitations

1. The AI model is only as good as the curated labels.
2. Synthetic ML demo data is only for pipeline testing; it is not scientific validation.
3. The classifier confidence is not the same as formal astronomical validation probability.
4. Crowded-field cases still require centroid/TPF/Gaia-style vetting for high-confidence claims.
5. Final planet claims require follow-up or cross-validation with known catalogs; this pipeline should output candidates and classifications, not discoveries by itself.
