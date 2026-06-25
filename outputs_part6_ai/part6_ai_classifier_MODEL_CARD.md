# Part 6 AI Classifier Model Card

## Intended use
This supervised model classifies candidate light-curve dips after Parts 1-5 have already extracted physical and statistical features. It should not be used directly on raw light curves, and it should not be treated as final astronomical validation.

## Classes
- `PLANETARY_TRANSIT_CANDIDATE`
- `ECLIPSING_BINARY`
- `BLEND_OR_CONTAMINATED_SIGNAL`
- `STELLAR_VARIABILITY`
- `INSTRUMENTAL_OR_LOW_QUALITY_SYSTEMATIC`
- `NO_SIGNIFICANT_SIGNAL`
- `UNCERTAIN_TRANSIT_LIKE_SIGNAL`

## Training data summary
- Rows: 315
- Features: 53
- Class counts: {'BLEND_OR_CONTAMINATED_SIGNAL': 45, 'ECLIPSING_BINARY': 45, 'INSTRUMENTAL_OR_LOW_QUALITY_SYSTEMATIC': 45, 'NO_SIGNIFICANT_SIGNAL': 45, 'PLANETARY_TRANSIT_CANDIDATE': 45, 'STELLAR_VARIABILITY': 45, 'UNCERTAIN_TRANSIT_LIKE_SIGNAL': 45}
- Calibrated probabilities: False
- Holdout evaluation used: True

## Evaluation
- Holdout / evaluation accuracy: 0.9367
- Balanced accuracy: 0.9372
- Macro F1: 0.9372

## Top features
- `vet_centroid_shift_pix`: 0.07659
- `vet_data_quality_score`: 0.05697
- `duration_days`: 0.05119
- `fit_duration_days`: 0.04862
- `snr`: 0.04582
- `sde`: 0.04346
- `class_systematic_score`: 0.04087
- `vet_centroid_shift_sigma`: 0.03349
- `fit_duration_err_days`: 0.03267
- `class_blend_score`: 0.03229
- `fit_snr`: 0.03142
- `vet_secondary_depth_ppm`: 0.03042
- `class_eb_score`: 0.02917
- `local_snr`: 0.02722
- `fit_rp_over_rstar`: 0.02480

## Guardrails
At prediction time, the package can blend AI probabilities with the rule-based scientific vetter and apply hard physical guardrails for strong secondary eclipses, odd/even mismatches, centroid shifts, low data quality, and low SNR.

## Limitations
This model learns the label quality and class definitions of the provided curated dataset. It should be validated on held-out real TESS targets, known planets, known eclipsing binaries, synthetic injections, and negative controls before being used for scientific claims.
