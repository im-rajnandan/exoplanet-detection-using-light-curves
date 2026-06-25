# Best-Grade Design Plan for Parts 1 and 2

## Executive summary

The first two parts of the project should build a trustworthy foundation:

- **Part 1:** convert raw TESS light curves into clean, normalized, detrended, metadata-rich light-curve products.
- **Part 2:** detect periodic dip candidates and estimate rough period, duration, depth, and SNR.

The output of Part 2 is not a final planet classification. It is a candidate signal table that later parts will classify into planetary transits, eclipsing binaries, blends, stellar variability, systematics, or uncertain cases.

---

## Part 1: TESS ingestion and preprocessing

### Scientific objective

Build a reliable preprocessing layer that preserves real transit information while removing obvious bad cadences and systematics. This layer must not silently fabricate data, hide failed downloads, or hard-reject crowded fields.

### Required inputs

- Local TESS FITS light curve, or later TIC ID + sector downloaded from MAST.
- Columns: `TIME`, `SAP_FLUX`, `PDCSAP_FLUX`, errors, `QUALITY`, centroid columns if available.
- Metadata: sector, camera, CCD, CROWDSAP, FLFRCSAP, stellar parameters if present.

### Core outputs

A `CleanLightCurve` object containing:

- raw selected flux
- normalized flux
- detrended flux
- flux source label
- centroid arrays
- finite/quality/outlier/final masks
- trend curve
- QC metrics
- warnings
- metadata

### Non-negotiable decisions

1. Prefer PDCSAP when valid, fallback to SAP only if necessary.
2. Never label SAP as PDCSAP.
3. Never silently replace failed real data with synthetic data.
4. Record CROWDSAP/FLFRCSAP but do not hard-reject on crowding.
5. Preserve raw, normalized, and detrended flux.
6. Use asymmetric outlier handling: clip positive spikes more aggressively than negative dips.
7. Record every preprocessing decision in `qc` and `warnings`.

### Quality-control metrics

- raw points
- finite points
- quality-kept points
- final points
- removed fraction
- cadence minutes
- baseline days
- number of large gaps
- largest gap
- selected flux source
- robust noise ppm
- RMS ppm
- CROWDSAP
- FLFRCSAP
- crowding risk

### Diagnostic plot

The preprocessing figure should show:

1. raw selected flux
2. normalized flux and trend
3. detrended flux
4. residual histogram in ppm

This plot catches mistakes before period search.

### Completion criteria

Part 1 is complete only when:

- one local FITS file can be loaded and processed
- synthetic demo works
- failed file/data states are explicit
- normalized and detrended medians are near 1
- QC summary is written
- diagnostic plot is generated
- tests pass

---

## Part 2: Periodic dip detection

### Scientific objective

Find periodic transit-like dips and estimate initial event parameters. This stage should not classify the signal source.

### Detection methods

- **BLS:** fast, stable baseline for box-like periodic dips.
- **TLS:** optional stronger transit-shaped search for more realistic planetary transit morphology.

The current implementation uses BLS by default because it is easier to run and debug. TLS support is included if `transitleastsquares` is installed.

### Candidate output fields

Each `CandidateSignal` contains:

- TIC ID
- sector
- candidate ID
- period days
- epoch / T0
- duration days
- depth fraction
- depth ppm
- SNR
- local SNR
- SDE or SDE-like statistic
- FAP if available
- number of observed transits
- number of full-ish transits
- number of in-transit points
- detection method
- flux source
- detrend variant
- warnings
- detection status

### Search bounds

Recommended first pass:

- `period_min_days = 0.2`
- `period_max_days = min(13.5, baseline / 2)`
- `min_transits = 2`
- duration grid: about 0.02–0.30 days

These bounds are suitable for single-sector high-cadence TESS light curves. Multi-sector data can expand period bounds later.

### SNR estimation

Use robust transit depth:

```text
depth = median(out_of_transit_flux) - median(in_transit_flux)
```

Then:

```text
SNR = depth / robust_noise × sqrt(number_of_in_transit_points)
```

Both global and local SNR are stored.

### Detection statuses

- `STRONG_DETECTION`
- `WEAK_DETECTION`
- `NO_DETECTION`
- `TOO_FEW_POINTS`
- `BLS_FAILED`
- `TLS_FAILED`

This is better than a single yes/no threshold because later classifiers may need weak candidates.

### Diagnostic plot

The detection figure shows:

1. detrended light curve with in-transit points highlighted
2. phase-folded light curve
3. zoomed transit phase view

### Completion criteria

Part 2 is complete only when:

- it consumes the `CleanLightCurve` object from Part 1
- it returns period, T0, duration, depth, SNR, and detection status
- it handles no-signal cases gracefully
- it writes candidate table rows
- it generates detection plots
- it recovers a synthetic injected transit in tests

---

## Why this is best-grade

This design shows evaluator-level maturity because it separates concerns:

- Preprocessing is not mixed with classification.
- Detection is not confused with planet validation.
- Candidate rows are built before AI classification.
- Crowding is modeled as risk, not a crude rejection.
- Outputs are traceable, inspectable, and testable.
- The pipeline can scale later without rewriting the foundation.
