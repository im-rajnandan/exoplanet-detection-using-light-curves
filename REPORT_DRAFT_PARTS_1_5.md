# Draft Report Text: Hybrid Pipeline for Exoplanet Transit Detection and Classification

## Methodology

We developed a modular, physics-informed AI pipeline for detecting and classifying transit-like events in noisy TESS light curves. The pipeline separates the problem into five stages: data ingestion and preprocessing, periodic dip detection, first-pass transit parameter refinement, scientific vetting feature extraction, and baseline classification. This separation prevents the classifier from operating directly on unverified raw light curves and makes every predicted class traceable to measurable evidence.

In preprocessing, each TESS light curve is loaded with its available SAP/PDCSAP flux, flux uncertainties, quality flags, centroid coordinates, and crowding metadata. PDCSAP is preferred when valid, but SAP fallback is allowed and explicitly recorded. Quality flags, non-finite values, positive outliers, cadence gaps, and noise metrics are tracked. The flux is normalized around unity and detrended using conservative rolling-median or optional biweight filtering. Raw, normalized, and detrended arrays are all preserved.

Periodic dips are detected using BLS/TLS when available, with a dependency-free periodic box-search fallback for minimal environments. For each candidate signal, the pipeline estimates the orbital period, epoch, duration, depth, number of observed transit events, and SNR. Detection is intentionally separated from classification: Part 2 only proposes candidate events, while later stages decide whether the event is planetary or a false-positive class.

For candidate refinement, the period and epoch are locally optimized by maximizing box-transit SNR. Event-level depths are estimated using local out-of-transit baselines, and depth uncertainty is estimated by bootstrap over transit events when possible. The pipeline reports Rp/Rstar from the transit depth and reports physical planet radius only if the stellar radius is available.

For classification, the pipeline extracts scientific vetting features: odd/even depth mismatch, secondary eclipse significance, centroid shift, CROWDSAP/FLFRCSAP crowding risk, dilution-corrected depth, transit morphology, red-noise proxy, and data-quality score. A transparent rule-based classifier then assigns one of the classes: planetary transit candidate, eclipsing binary, blend/contaminated signal, stellar variability, instrumental/systematic, uncertain, or no significant signal. This rule-based classifier is intended as the baseline that will later be compared against a supervised AI classifier trained on curated labels.

## Uncertainty estimation

The transit SNR is estimated as the transit depth divided by robust local out-of-transit scatter and scaled by the square root of the number of in-transit points. Depth uncertainty is estimated from event-level bootstrapping when multiple transits are observed. Period and epoch uncertainties are approximated from the transit duration, time baseline, and SNR. Classification confidence is derived from a combination of detection strength and physical false-positive evidence, including secondary eclipse, odd/even, centroid, crowding, and data-quality terms.

## Assumptions and limitations

The current parameter-refinement stage uses a robust box/profile model rather than a full physical Mandel-Agol transit model. This is appropriate for first-pass candidate ranking but should be replaced by physical model fitting for final astrophysical characterization. CROWDSAP is treated as contamination evidence, not proof of a blend. Centroid diagnostics are based on light-curve centroid columns; high-confidence crowded-field validation should later include target pixel file difference imaging and Gaia nearby-source analysis. The baseline classifier is intentionally transparent and should be upgraded using the curated labeled dataset in the AI classification stage.
