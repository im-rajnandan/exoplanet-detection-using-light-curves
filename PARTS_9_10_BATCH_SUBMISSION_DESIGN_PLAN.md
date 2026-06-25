# Parts 9–10 Design Plan: Batch Processing, Final Catalog, and Submission Assets

## Purpose
Parts 1–8 build the scientific engine: preprocessing, detection, fitting, vetting, rule-based classification, AI classification, uncertainty estimation, and validation. Parts 9–10 turn that engine into a deliverable system that can process a sector-scale collection of TESS light curves and produce evaluator-facing outputs.

## Part 9: Sector-scale batch processing

### Goals
- Process thousands to tens of thousands of light curves without manual intervention.
- Never lose completed targets when a long run is interrupted.
- Separate successful targets, failed targets, no-signal targets, and candidate-producing targets.
- Produce a raw internal catalog and a harmonized final science catalog.

### Batch architecture
The batch manager processes either:
1. a list of local FITS files, or
2. a list of already-loaded `RawLightCurve` objects.

For each target it runs:

```text
Part 1 preprocessing
→ Part 2 detection
→ Part 3 parameter refinement
→ Part 4 vetting features
→ Part 5 rule-based classifier
→ Part 6 optional AI classifier
→ Part 7 uncertainty/confidence
→ Part 8 validation-ready candidate row
```

### Reliability design
The batch system writes per-target cached catalog rows immediately after each target finishes. If the process stops, `resume=True` reuses completed per-target outputs instead of rerunning everything.

Generated files:

```text
batch_run_manifest.json
batch_raw_candidate_catalog.csv
batch_final_candidate_catalog.csv
batch_target_summary.csv
batch_failure_log.csv
batch_final_summary.json
cache/<target_key>_catalog.csv
cache/<target_key>_summary.json
```

### Failure handling
Each target has an independent error boundary. A failed FITS file or unusable light curve is written into the failure log rather than crashing the entire sector run. This is important for real survey data, where some files may be missing columns, corrupted, too short, saturated, or dominated by systematics.

### Resume/caching policy
A target is skipped on rerun if both its per-target catalog and summary exist in cache. This makes long sector experiments reproducible and interrupt-safe.

## Part 10: Final outputs and submission package

### Final candidate catalog
The internal catalog contains many prefixes: `fit_*`, `vet_*`, `class_*`, `ai_*`, and `unc_*`. Part 10 creates a compact evaluator-friendly catalog with stable columns:

```text
tic_id
sector
candidate_id
science_priority_rank
science_priority_score
final_science_class
final_science_confidence
confidence_level
recommended_action
period_days
period_err_days
epoch_time
epoch_err_days
duration_hours
duration_err_hours
depth_ppm
depth_err_ppm
snr
effective_snr
n_transits
n_full_transits
detection_method
selected_flux_source
crowdsap
crowding_risk
secondary_sigma
odd_even_sigma
centroid_shift_sigma
data_quality_score
evidence_summary
risk_summary
```

The priority score is not a validation probability. It is a triage score for human review and follow-up.

### Final visualizations
The final output layer produces:

```text
final_class_distribution.png
final_confidence_distribution.png
final_period_depth_priority.png
submission_candidate_review.md
submission_three_page_report_draft.md
submission_summary.json
```

### Report strategy
The 3-page report draft is organized around the evaluator criteria:

1. Methodology: preprocessing, detection, fitting, vetting, AI classification.
2. SNR/significance and uncertainty estimation.
3. Validation metrics, outputs, assumptions, and limitations.

The report is deliberately honest: classifier confidence is not claimed to be formal exoplanet validation probability, and crowded/high-priority candidates still require TPF/Gaia-style follow-up.

## Best-grade behavior
A weak project stops at “we ran a detector.” This project produces:

- a traceable preprocessing layer,
- candidate-level detection outputs,
- scientifically meaningful vetting features,
- supervised AI probabilities with physical guardrails,
- uncertainty estimates,
- validation metrics,
- resume-safe sector-scale processing,
- final candidate catalog,
- final visual summary,
- and a concise report draft.
