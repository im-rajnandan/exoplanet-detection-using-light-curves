# Report Draft: AI-enabled Detection and Classification of Exoplanet-like Dips in TESS Light Curves

## Methodology

We developed a modular, physics-informed AI pipeline for detecting and classifying transit-like dips in noisy TESS light curves. The pipeline first ingests TESS light-curve products, selects a valid SAP/PDCSAP flux source, applies quality masking, normalizes the flux, detrends long-timescale variability, records metadata such as CROWDSAP/FLFRCSAP, and computes noise and data-quality metrics. The cleaned light curve is then searched for periodic box/transit-like dips using a BLS/TLS-compatible detection layer. For each candidate signal, the pipeline estimates orbital period, epoch, duration, transit depth, number of observed transits, and signal-to-noise ratio.

The candidate is then refined and vetted using astrophysically motivated diagnostics: event-by-event depth consistency, odd/even transit depth comparison, secondary-eclipse search around phase 0.5 and nearby phases, centroid-shift analysis, crowding/dilution features from CROWDSAP, transit morphology, red-noise proxy, and overall data quality. These features feed a transparent rule-based classifier and, when labeled curated data are available, a supervised AI classifier. The classifier outputs class probabilities for planetary transits, eclipsing binaries, blended/contaminated signals, stellar variability, instrumental/systematic cases, no-signal cases, and uncertain transit-like events.

## Uncertainty and confidence

Uncertainties are estimated at multiple levels. Detection confidence combines transit SNR, SDE-like periodogram strength, number of full transits, and data quality. Parameter uncertainty is estimated from local photometric noise, event-to-event depth scatter, residual bootstrap resampling, and detrending stability. Red noise is handled through a beta inflation factor based on how the light-curve scatter bins down on a transit-duration timescale. Classification confidence is taken from the AI model probability or rule-based confidence and adjusted using the probability margin between the top classes.

The final confidence level combines detection, parameter, and classification confidence. Each candidate is assigned a confidence level of HIGH, MEDIUM, LOW, or VERY_LOW. This prevents overclaiming: a high-SNR transit-like event in a crowded aperture with centroid motion is not reported as a high-confidence planet, even if periodic dips are detected.

## Validation

The validation framework supports both organizer-provided curated labels and synthetic injection-recovery experiments. Detection validation reports precision, recall, specificity, F1, and TP/FP/TN/FN counts. Classification validation reports accuracy, balanced accuracy, macro F1, weighted F1, confusion matrix, and per-class metrics. Parameter validation reports period, depth, and duration recovery errors, including median relative absolute error and fractions recovered within 1%, 5%, and 10%. Reliability validation compares reported confidence with empirical accuracy using confidence bins.

Before the curated dataset is available, a synthetic injection-recovery grid is used to test the end-to-end wiring. The grid includes planet-like transits, eclipsing binaries with secondary eclipses, and blended/contaminated signals with centroid shifts and low CROWDSAP. These tests are not treated as a substitute for real validation; they are used to verify that the pipeline, metrics, diagnostics, and outputs work correctly.

## Assumptions and limitations

The current transit fit is a robust first-pass box/profile refinement, not a full physical Mandel-Agol fit. Planet radius in Earth radii is only reported when stellar radius is available; otherwise the pipeline reports radius ratio. CROWDSAP is treated as a contamination-risk feature rather than a hard rejection rule. The AI classifier should be retrained and calibrated on the organizer's curated labeled dataset before final science-dataset predictions are submitted. Crowded-field candidates with high scientific value should ideally receive target-pixel-file or Gaia-based follow-up vetting.

## Current outputs

The Parts 1–8 implementation produces a candidate catalog, uncertainty columns, validation JSON/Markdown reports, confusion matrix, parameter-recovery plot, reliability diagram, and injection-recovery heatmap. The design is modular so that later full-sector batch processing and final report generation can be added without rewriting the core science pipeline.
