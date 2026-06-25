# Parts 7–8 Design Plan: Uncertainty, Confidence, and Validation

## Why these parts matter

Parts 1–6 build the pipeline: ingestion, preprocessing, detection, parameter refinement, vetting, rule-based classification, and supervised AI. Parts 7–8 answer the evaluator's most important question: **how much should we trust the result?**

The problem statement explicitly asks for signal-to-noise or significance levels, parameter estimates, confidence levels, and accuracy. Therefore the project must not only output a class; it must quantify detection confidence, parameter uncertainty, classifier reliability, and validation performance.

## Part 7: Uncertainty and confidence estimation

Part 7 estimates uncertainty at three levels:

1. **Detection uncertainty**
   - Uses transit SNR, SDE-like detection statistic, number of full transits, and data-quality score.
   - Inflates SNR under red noise using a beta factor based on how noise bins down on a transit-duration timescale.

2. **Parameter uncertainty**
   - Period/T0/duration uncertainties from the local ephemeris/grid refinement layer.
   - Depth uncertainty from three sources: formal local noise, residual bootstrap, and event-to-event depth scatter.
   - Final reported depth uncertainty is conservative: the maximum finite estimate, inflated for red noise.

3. **Classification uncertainty**
   - Uses rule-based confidence or AI final probability if the supervised model is available.
   - Uses class-probability margin where available. A high-probability prediction with a tiny margin is treated as less reliable.

The final confidence combines:

```text
final_confidence = 0.35*detection_confidence
                 + 0.30*parameter_confidence
                 + 0.35*classification_confidence
```

The output confidence level is one of:

```text
HIGH, MEDIUM, LOW, VERY_LOW
```

The implementation is in:

```text
src/exoplanet_pipeline/uncertainty.py
```

Main functions:

```python
estimate_candidate_uncertainty(...)
add_uncertainty_columns(...)
estimate_red_noise_beta(...)
residual_bootstrap_depth_uncertainty(...)
estimate_multidetrender_stability(...)
```

## Part 8: Validation framework

Part 8 evaluates the complete pipeline against labeled data. It supports both the organizer's curated dataset and synthetic injection-recovery experiments.

Validation is split into four blocks:

### 1. Detection validation

This treats all non-quiet/non-no-signal classes as true signals. It reports:

```text
TP, FP, TN, FN
precision
recall
specificity
F1
```

### 2. Classification validation

This compares canonical labels against predicted classes and reports:

```text
accuracy
balanced accuracy
macro F1
weighted F1
macro precision
macro recall
confusion matrix
classification report
```

### 3. Parameter validation

If true/injected parameters are known, it compares:

```text
period
transit depth
transit duration
```

and reports:

```text
MAE
median absolute error
RMSE
median relative absolute error
within 1%, 5%, and 10%
```

### 4. Reliability / calibration validation

If confidence values and labels are available, it bins confidence values and compares:

```text
reported mean confidence vs empirical accuracy
```

This produces an expected calibration error (ECE) approximation.

Implementation files:

```text
src/exoplanet_pipeline/validation.py
src/exoplanet_pipeline/validation_diagnostics.py
src/exoplanet_pipeline/injection_recovery.py
```

## Synthetic injection-recovery

Before the curated dataset arrives, we need a way to prove the full pipeline works. The injection-recovery module generates synthetic planet, EB, and blend-like cases with varied:

```text
period
depth
duration
noise level
crowding/CROWDSAP
centroid shift
secondary eclipse depth
```

It then runs the actual Parts 1–5 pipeline and attaches Part 7 uncertainty, producing a candidate catalog with known ground truth.

The goal is not to perfectly simulate the sky. The goal is to test whether the pipeline wiring, metrics, confidence, validation tables, and plots are functioning correctly.

## Outputs produced

The demo script:

```text
scripts/run_parts_7_8_synthetic_validation.py
```

writes:

```text
outputs_parts_7_8/
  parts_7_8_injection_recovery_catalog.csv
  parts_7_8_injection_recovery_summary.json
  parts_7_8_validation_report.json
  parts_7_8_validation_report.md
  parts_7_8_confusion_matrix.png
  parts_7_8_parameter_recovery.png
  parts_7_8_reliability_diagram.png
  parts_7_8_injection_heatmap.png
```

## How this connects to the full project

The connected system is now:

```text
Raw TESS light curve
  → Part 1: ingestion + preprocessing
  → Part 2: periodic dip detection
  → Part 3: parameter refinement
  → Part 4: vetting feature extraction
  → Part 5: rule-based classifier
  → Part 6: supervised AI classifier when curated labels are available
  → Part 7: uncertainty and confidence estimation
  → Part 8: validation framework and injection recovery
```

This is the first version that is not just a detector/classifier, but a scientifically evaluable pipeline.
