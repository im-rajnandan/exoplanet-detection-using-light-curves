# Parts 3–5 Design Plan: Parameter Refinement, Vetting Features, and Baseline Classification

This document extends the Parts 1–2 foundation into the scientific layer that makes the project evaluator-ready.

## Why Parts 3–5 matter

After Part 2, the pipeline only knows that a periodic dip may exist. It does not yet know whether the signal is a planetary transit, eclipsing binary, blend, stellar variability, or systematic artifact. Parts 3–5 convert a raw detection into a scientifically interpretable candidate.

The design principle is:

> Detection finds candidate dips; parameter fitting measures them; vetting explains them; classification labels them.

## Part 3: First-pass transit parameter refinement

### Inputs

- `CleanLightCurve` from Part 1
- `CandidateSignal` from Part 2

### Outputs

A `TransitFitResult` containing:

- refined period
- refined epoch/T0
- refined duration
- refined depth
- period uncertainty
- epoch uncertainty
- duration uncertainty
- depth uncertainty
- SNR
- Rp/Rstar
- Rp in Earth radii only if stellar radius is available
- event-by-event depth table

### Method used in the package

The current implementation uses a dependency-light robust box-profile refinement:

1. Perform a local grid search around the detected period and epoch.
2. Maximize box-transit SNR.
3. Estimate event-level depths using local baselines around each transit.
4. Estimate duration using half-depth width in the phase-folded profile.
5. Estimate depth uncertainty by event bootstrap if multiple transit events exist.
6. Estimate rough period and epoch uncertainties from duration, baseline, and SNR.

This is intentionally not presented as a final physical Mandel-Agol model. It is a robust first-pass parameter estimator suitable for the competition pipeline and later ML features.

### Why this is scientifically safer

A first-pass detector can return slightly biased period, duration, or depth. If we pass those directly into classification, secondary eclipse and odd/even tests can fail. Refining the ephemeris improves downstream vetting.

### Important assumptions

- Transit is approximately periodic over the observed baseline.
- First-pass transit shape can be approximated by a box/profile model.
- Event-level scatter is a useful uncertainty proxy.
- Planet radius is not reported unless stellar radius exists.

## Part 4: Vetting feature extraction

### Inputs

- `CleanLightCurve`
- `CandidateSignal`
- `TransitFitResult`

### Outputs

A `VettingFeatures` object containing:

- odd/even depth difference and significance
- secondary eclipse depth, phase, and significance
- centroid shift in pixels and sigma
- CROWDSAP/FLFRCSAP and crowding risk
- dilution-corrected depth estimate
- shape/morphology proxy
- out-of-transit RMS
- red-noise proxy
- data-quality score
- warnings and evidence flags

### Implemented vetting tests

#### 1. Odd/even depth test

Eclipsing binaries often appear at half the true orbital period. In that case, alternating dips have different depths. The pipeline estimates a depth for each event and compares odd and even events.

Output:

- `odd_depth_ppm`
- `even_depth_ppm`
- `odd_even_sigma`
- `odd_even_depth_diff_ppm`

#### 2. Secondary eclipse test

The pipeline correctly treats primary transit as phase 0 and searches for secondary eclipse near phase 0.5, while also scanning phases 0.15–0.85 for eccentric binary cases.

This explicitly avoids the common mistake of accidentally selecting the primary transit window as the secondary eclipse.

Output:

- `secondary_depth_ppm`
- `secondary_sigma`
- `secondary_phase`
- `secondary_to_primary_ratio`

#### 3. Centroid shift test

Centroid coordinates are detrended by subtracting a rolling trend, not by flux-style division. The in-transit centroid residual is compared with the out-of-transit residual.

Output:

- `centroid_shift_pix`
- `centroid_shift_sigma`

This is crucial for identifying background blends.

#### 4. Crowding/dilution features

CROWDSAP is treated as risk evidence, not a hard rejection.

Output:

- `crowdsap`
- `flfrcsap`
- `crowding_risk = 1 - CROWDSAP`
- `corrected_depth_ppm = observed_depth / CROWDSAP`

#### 5. Shape and variability features

The package includes simple morphology and red-noise features:

- `v_shape_score`
- `transit_asymmetry`
- `out_of_transit_rms_ppm`
- `red_noise_proxy`

These are not final astrophysical truth, but they are useful classifier features.

## Part 5: Transparent rule-based baseline classifier

### Purpose

Before training the AI model, we need a scientifically explainable baseline. This gives:

- a working classifier before curated labels arrive
- interpretable evidence strings for reports
- sanity checks for the future ML model
- a feature/label interface that the AI model can later replace or blend with

### Classes

The baseline classifier outputs:

- `PLANETARY_TRANSIT_CANDIDATE`
- `ECLIPSING_BINARY`
- `BLEND_OR_CONTAMINATED_SIGNAL`
- `STELLAR_VARIABILITY`
- `INSTRUMENTAL_OR_LOW_QUALITY_SYSTEMATIC`
- `UNCERTAIN_TRANSIT_LIKE_SIGNAL`
- `NO_SIGNIFICANT_SIGNAL`

### Evidence used

Planet candidate evidence:

- high SNR
- high SDE if available
- multiple observed events
- low secondary evidence
- low odd/even evidence
- clean centroid
- acceptable crowding
- good data quality

Eclipsing binary evidence:

- significant secondary eclipse
- odd/even mismatch
- very deep event
- large Rp/Rstar
- triangular/poorly flat-bottom morphology

Blend evidence:

- significant centroid shift
- low CROWDSAP / high crowding risk
- large dilution correction

Stellar variability evidence:

- high red-noise proxy
- broad/quasi-periodic dips

Systematic evidence:

- low data quality
- few full transits
- non-positive or unstable depth

### Why rule-based first?

A black-box classifier trained too early can learn preprocessing bugs or synthetic artifacts. The rule-based classifier forces us to define the physical evidence clearly. Later, the supervised AI model should consume the same candidate/fit/vetting table.

## Current implementation files

```text
src/exoplanet_pipeline/fit.py
src/exoplanet_pipeline/vetting.py
src/exoplanet_pipeline/classify.py
src/exoplanet_pipeline/pipeline.py
scripts/run_parts_1_to_5_synthetic.py
scripts/run_parts_1_to_5_fits.py
tests/test_fit_vetting_classify.py
```

## Acceptance criteria for Parts 3–5

Parts 3–5 are considered working when:

1. A detected candidate gets refined period, epoch, duration, depth, and SNR.
2. Event-level depths are stored.
3. A primary-only planet does not get falsely flagged as having a secondary eclipse.
4. A synthetic eclipsing binary gets a high secondary-eclipse significance.
5. A synthetic blend with centroid motion gets a high blend score.
6. CROWDSAP is used as contamination risk, not automatic rejection.
7. The output catalog contains candidate, fit, vetting, and classification columns.
8. A diagnostic plot summarizes the final evidence.

## Next step after this

Part 6 should train a supervised AI classifier on the curated dataset. The curated labels should not be used to rewrite preprocessing; they should be used to learn class probabilities from the feature table produced by Parts 1–5.
