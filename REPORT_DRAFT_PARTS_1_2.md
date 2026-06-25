# Report Draft: Parts 1 and 2 Methodology

## Methodology summary

We implemented the first two stages of a hybrid physics-informed AI pipeline for noisy TESS light curves. The first stage converts raw TESS light curves into standardized clean light-curve products. The second stage searches these products for statistically significant periodic dips and reports candidate-level signal parameters.

## Part 1: Preprocessing

For each light curve, the loader extracts time, SAP flux, PDCSAP flux, flux errors, quality flags, centroid columns, and metadata such as sector, camera, CCD, CROWDSAP, and FLFRCSAP. PDCSAP flux is preferred when valid because it has common-mode systematics removed, but SAP flux is used as a fallback when PDCSAP is missing or invalid. The selected flux source is explicitly recorded and never relabeled.

Cadences with invalid time/flux values and severe quality flags are removed. The selected flux is normalized by its median, positive outliers are clipped conservatively, and negative outliers are only flagged by default because transit signals are negative events. A robust rolling-median detrending step removes slow variability while preserving the raw, normalized, and detrended versions for later comparison. The preprocessing stage also computes quality metrics including number of clean cadences, removed fraction, cadence, baseline, gap statistics, robust noise in ppm, CROWDSAP, FLFRCSAP, and crowding risk.

A key assumption is that preprocessing should not decide final astrophysical class. In particular, low CROWDSAP is treated as contamination evidence, not an automatic rejection, because the problem specifically includes crowded-field light curves.

## Part 2: Periodic dip detection

The cleaned light curve is searched for periodic transit-like dips using a Box Least Squares baseline detector. TLS support is included for transit-shaped searches when the `transitleastsquares` package is available. The period grid is set from 0.2 days to the smaller of 13.5 days or half the time baseline, which is appropriate for single-sector TESS searches requiring at least two transits. A grid of plausible transit durations is searched.

For each candidate, the pipeline reports period, epoch, duration, depth, depth in ppm, global SNR, local SNR, SDE-like periodogram significance, number of observed transits, and number of in-transit data points. Transit SNR is estimated as the robust transit depth divided by local out-of-transit scatter, scaled by the square root of the number of in-transit points.

The detection stage intentionally does not classify the signal as a planet, eclipsing binary, blend, or stellar variability. It outputs candidate signals. Later stages will extract vetting features such as odd/even depth differences, secondary eclipses, centroid shifts, crowding features, shape metrics, and stellar variability features before applying the AI classifier.

## Current deliverables

The implementation includes modular source code, a synthetic demo, local FITS preprocessing, candidate detection, preprocessing plots, detection plots, candidate output tables, and unit tests. This forms the foundation for later classification and validation stages.
