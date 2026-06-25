# AI-enabled Detection of Exoplanets from Noisy TESS Light Curves

## 1. Methodology
We implemented a hybrid physics-informed and AI-driven pipeline for TESS light curves. The pipeline first ingests SAP/PDCSAP light curves, applies TESS quality masking, selects the safest flux source, normalizes the flux, performs conservative detrending, and records quality-control metrics such as cadence, baseline, noise, gap fraction, CROWDSAP, FLFRCSAP, and centroid availability. Synthetic fallback is disabled for real science data so failed downloads cannot become false successes.

Periodic transit-like dips are detected with a BLS/TLS-style candidate search. Each candidate is represented by period, epoch, duration, depth, SNR, periodogram strength, number of observed transits, and detection status. Candidate detection is deliberately separated from classification: the detector only answers whether a periodic dip exists, while later vetting decides whether it resembles a planet, eclipsing binary, blend, stellar variability, systematic, or uncertain signal.

For each candidate we refine period, epoch, duration, and depth using a local box-profile fit and event-by-event depth estimates. We then extract physically motivated vetting features: odd/even depth mismatch, secondary-eclipse strength at phase 0.5, centroid shift significance, crowding/dilution risk, V-shape score, harmonic risk, red-noise proxy, and data-quality score. These features feed both a transparent rule-based classifier and an optional supervised classifier trained on curated labeled candidate catalogs.

## 2. Classification and uncertainty
The classifier outputs probabilities for planetary transit candidate, eclipsing binary, blend/contaminated signal, stellar variability, instrumental/systematic, no significant signal, and uncertain transit-like signal. Physical guardrails prevent the AI model from overcalling planet candidates when strong secondary eclipses, odd/even mismatch, centroid shifts, or poor data quality are present.

Signal significance is reported mainly through local transit SNR, periodogram strength, and effective SNR after red-noise inflation. Parameter uncertainties combine local photometric scatter, residual bootstrap depth uncertainty, event-to-event depth scatter, ephemeris-grid curvature, and multi-detrender stability. Final confidence is a weighted combination of detection confidence, parameter confidence, and classification confidence; it is a triage confidence, not a formal astronomical validation probability.

## 3. Validation and outputs
The validation layer supports curated labeled data and synthetic injection-recovery experiments. Detection is evaluated with precision, recall, specificity, and F1. Classification is evaluated with accuracy, balanced accuracy, macro F1, weighted F1, and a confusion matrix. Parameter recovery is measured through absolute and relative errors in period, depth, and duration. Confidence calibration is checked through reliability bins comparing reported confidence with empirical correctness.

Current candidate-catalog summary: **3 candidates** across **3 targets**. Class counts: `{"PLANETARY_TRANSIT_CANDIDATE": 1, "ECLIPSING_BINARY": 1, "BLEND_OR_CONTAMINATED_SIGNAL": 1}`.

Validation snapshot, when labels are available: detection metrics `{}`; classification metrics `{}`. Parameter metrics are stored for period, depth, and duration recovery when ground truth columns are available.

## Assumptions and limitations
We assume that periodic dips are approximately stable over the observed baseline and that detrending windows are longer than the transit duration. Transit depth may be biased by dilution in crowded apertures; CROWDSAP is therefore treated as a risk feature rather than an automatic rejection. Planet radius is only physically meaningful when reliable stellar radius is available. Crowded-field and high-value candidates should receive follow-up inspection using target-pixel difference imaging and nearby-source checks before being treated as validated planets.
