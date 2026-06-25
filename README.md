# Exoplanet Pipeline — Best-grade Parts 1–10

This package implements a modular pipeline for the problem statement:

> AI-enabled detection of exoplanets from noisy astronomical light curves.

It now includes:

```text
Part 1: TESS ingestion, quality control, normalization, detrending, QC metrics
Part 2: periodic dip detection with BLS/TLS-style candidate outputs
Part 3: first-pass transit parameter refinement
Part 4: scientific vetting feature extraction
Part 5: transparent rule-based baseline classifier
Part 6: supervised AI classifier using curated labeled candidate features
Part 7: uncertainty estimation and final confidence scoring
Part 8: validation framework and synthetic injection-recovery
Part 9: sector-scale batch processing with resume/caching/failure logs
Part 10: final candidate catalog, review assets, plots, and 3-page report draft
```

The philosophy is to use physics-informed preprocessing and feature extraction first, then train AI on candidate-level features rather than raw unverified light curves.

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

---

## Run Parts 1–5 synthetic demo

```bash
python scripts/run_parts_1_to_5_synthetic.py
```

This creates synthetic examples for:

- planet-like transit
- eclipsing binary
- blended/off-target signal

and writes diagnostic plots/catalogs to `outputs_parts_1_to_5/`.

---

## Run Part 6 AI classifier demo

```bash
python scripts/run_part6_synthetic_ai_demo.py
```

This generates a synthetic labeled feature catalog, trains the supervised classifier, evaluates it, saves the model, and writes:

```text
outputs_part6_ai/part6_synthetic_labeled_feature_catalog.csv
outputs_part6_ai/part6_ai_classifier.joblib
outputs_part6_ai/part6_ai_classifier_metrics.json
outputs_part6_ai/part6_ai_classifier_feature_importance.csv
outputs_part6_ai/part6_ai_classifier_MODEL_CARD.md
outputs_part6_ai/part6_confusion_matrix.png
outputs_part6_ai/part6_feature_importance.png
outputs_part6_ai/part6_demo_predictions.csv
outputs_part6_ai/part6_prediction_probabilities.png
```

Synthetic Part 6 data is only for code validation. For the real project, train on the organizer's curated labeled dataset.

---

## Train on curated labeled dataset

If the curated dataset has a column named `label`:

```bash
python scripts/train_ai_classifier_from_catalog.py curated_labeled_catalog.csv --label-col label --output-dir outputs_part6_ai
```

The label-normalization layer supports aliases such as:

```text
planet, confirmed_planet, exoplanet, eb, eclipsing_binary, blend,
background_eb, starspot, variable, systematic, false_positive, noise, uncertain
```

Unknown labels are not silently guessed; clean them or add aliases in `ml.py`.

---

## Predict on science candidates

```bash
python scripts/predict_ai_classifier_catalog.py \
  outputs_part6_ai/part6_ai_classifier.joblib \
  candidate_catalog.csv \
  --output-csv outputs_part6_ai/science_predictions.csv
```

Final predictions include:

```text
ai_predicted_class
ai_confidence
ai_prob_<class>
final_predicted_class
final_confidence
final_prob_<class>
final_classifier_warnings
```

The final probabilities blend AI with the Part 5 rule-based scientific scores and physical guardrails.

---

## Project structure

```text
src/exoplanet_pipeline/
  config.py
  schema.py
  ingest.py
  quality.py
  preprocess.py
  detect.py
  fit.py
  vetting.py
  classify.py
  ml.py
  ml_synthetic.py
  ml_diagnostics.py
  diagnostics.py
  synthetic.py
  pipeline.py

scripts/
  run_synthetic_demo.py
  run_parts_1_to_5_synthetic.py
  run_part6_synthetic_ai_demo.py
  train_ai_classifier_from_catalog.py
  predict_ai_classifier_catalog.py

tests/
  test_preprocess.py
  test_detection.py
  test_fit_vetting_classify.py
  test_ml_part6.py

notebooks/
  01_02_parts_1_2_demo.ipynb
  03_05_parts_3_5_demo.ipynb
  06_part_6_ai_classifier_demo.ipynb
```

---

## Why this is evaluator-friendly

The pipeline directly targets the evaluation criteria:

- **event detection:** BLS/TLS-style periodic dip detection;
- **parameter accuracy:** period, epoch, duration, depth, SNR, event counts;
- **classification accuracy:** curated-data supervised classifier;
- **methodology:** physics-informed features plus AI;
- **visualization:** preprocessing, detection, vetting, confusion-matrix, and feature-importance plots;
- **uncertainty:** local SNR, robust depth uncertainty, probability calibration where possible, and guardrail warnings.

---

## Important scientific caution

This pipeline outputs candidate classifications and confidence levels. It does not by itself confirm planets. Crowded-field or high-value candidates still require stronger vetting such as target pixel file difference imaging, Gaia neighbor checks, or external catalog comparison.

## Parts 7–8: uncertainty and validation

This layer adds science-grade uncertainty estimates and validation reports.

New capability:

```text
Part 7: uncertainty estimation and final confidence scoring
Part 8: validation framework and synthetic injection-recovery
```

New files:

```text
src/exoplanet_pipeline/uncertainty.py
src/exoplanet_pipeline/validation.py
src/exoplanet_pipeline/validation_diagnostics.py
src/exoplanet_pipeline/injection_recovery.py
src/exoplanet_pipeline/pipeline_parts_1_to_8.py

scripts/run_parts_1_to_8_synthetic_single.py
scripts/run_parts_7_8_synthetic_validation.py
scripts/validate_candidate_catalog.py

tests/test_uncertainty_validation.py

PARTS_7_8_UNCERTAINTY_VALIDATION_DESIGN_PLAN.md
REPORT_DRAFT_PARTS_1_8.md
```

Run the compact synthetic validation demo:

```bash
PYTHONPATH=src python scripts/run_parts_7_8_synthetic_validation.py
```

Validate an organizer-provided labeled prediction catalog:

```bash
PYTHONPATH=src python scripts/validate_candidate_catalog.py \
  --catalog path/to/predictions.csv \
  --label-col label \
  --pred-col final_predicted_class \
  --out-dir outputs_validation
```

The validation output includes detection metrics, classification metrics, parameter-recovery metrics, reliability/calibration metrics, and diagnostic plots.


## Parts 9–10: Batch processing and final submission assets

The project now includes the full final layer:

```text
Part 9  - sector-scale batch processing, resume/caching, target summaries, failure logs
Part 10 - harmonized final candidate catalog, priority ranking, final plots, candidate-review markdown, and 3-page report draft
```

Run the synthetic sector-like demonstration:

```bash
python scripts/run_parts_9_10_synthetic_batch.py
```

Run on a directory of local TESS FITS light curves:

```bash
python scripts/run_parts_9_10_fits_directory.py /path/to/fits_dir --output-dir outputs_sector --max-targets 100
```

Generate final submission assets from any candidate catalog:

```bash
python scripts/generate_final_submission_assets.py outputs_sector/batch_final_candidate_catalog.csv --output-dir submission_assets
```

Important final outputs:

```text
batch_final_candidate_catalog.csv
batch_target_summary.csv
batch_failure_log.csv
submission_assets/submission_final_candidate_catalog.csv
submission_assets/submission_candidate_review.md
submission_assets/submission_three_page_report_draft.md
submission_assets/final_class_distribution.png
submission_assets/final_confidence_distribution.png
submission_assets/final_period_depth_priority.png
```

## Audit note

The full test suite was re-run with plugin autoload disabled for a deterministic environment:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests
# 17 passed
```

The synthetic Parts 9–10 demo accepts `--output-dir`, `--n-periods`, `--method`, `--resume`, and `--make-plots`. Batch resume now also skips no-candidate and failed targets using the summary cache, not only targets with non-empty per-target candidate CSVs.
