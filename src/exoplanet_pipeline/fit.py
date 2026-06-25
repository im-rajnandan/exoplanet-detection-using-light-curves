from __future__ import annotations

from dataclasses import asdict
import numpy as np
import pandas as pd

from .schema import CleanLightCurve, CandidateSignal, TransitFitResult
from .detect import make_transit_mask, transit_event_numbers
from .utils import robust_sigma


def _safe_float(x, default=np.nan) -> float:
    try:
        x = float(x)
        return x if np.isfinite(x) else float(default)
    except Exception:
        return float(default)


def phase_fold_time(time: np.ndarray, period: float, t0: float) -> np.ndarray:
    """Return folded time in days centered on transit, in [-P/2, P/2)."""
    return ((np.asarray(time, dtype=float) - t0 + 0.5 * period) % period) - 0.5 * period


def estimate_event_depths(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    duration: float,
    baseline_width_factor: float = 5.0,
) -> pd.DataFrame:
    """Estimate one robust depth per observed transit event.

    This is intentionally simple and dependency-light. It is not a full Mandel-Agol
    transit fit; it gives event-level diagnostics needed for odd/even tests,
    transit consistency, and uncertainty estimates.
    """
    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    finite = np.isfinite(time) & np.isfinite(flux)
    time = time[finite]
    flux = flux[finite]

    in_any = make_transit_mask(time, period, t0, duration, width_factor=1.0)
    near_any = make_transit_mask(time, period, t0, duration, width_factor=baseline_width_factor)
    event_ids = transit_event_numbers(time, period, t0)

    rows: list[dict] = []
    for eid in np.unique(event_ids[near_any | in_any]):
        event_center = t0 + eid * period
        local = np.abs(time - event_center) <= 0.5 * baseline_width_factor * duration
        in_tr = np.abs(time - event_center) <= 0.5 * duration
        out = local & (~in_tr)
        if in_tr.sum() < 3 or out.sum() < 6:
            rows.append({
                "event_id": int(eid),
                "event_center": float(event_center),
                "n_in": int(in_tr.sum()),
                "n_out": int(out.sum()),
                "depth_fraction": np.nan,
                "depth_ppm": np.nan,
                "depth_err_fraction": np.nan,
                "snr": np.nan,
                "coverage": "partial_or_sparse",
            })
            continue
        baseline = np.nanmedian(flux[out])
        in_flux = np.nanmedian(flux[in_tr])
        depth = baseline - in_flux
        noise = robust_sigma(flux[out] - np.nanmedian(flux[out]))
        depth_err = noise / np.sqrt(max(int(in_tr.sum()), 1)) if np.isfinite(noise) and noise > 0 else np.nan
        snr = depth / depth_err if np.isfinite(depth_err) and depth_err > 0 else np.nan
        rows.append({
            "event_id": int(eid),
            "event_center": float(event_center),
            "n_in": int(in_tr.sum()),
            "n_out": int(out.sum()),
            "depth_fraction": float(depth),
            "depth_ppm": float(depth * 1e6),
            "depth_err_fraction": float(depth_err),
            "snr": float(snr),
            "coverage": "ok" if in_tr.sum() >= 3 and out.sum() >= 10 else "partial",
        })
    return pd.DataFrame(rows)


def estimate_duration_from_folded_profile(
    time: np.ndarray,
    flux: np.ndarray,
    period: float,
    t0: float,
    initial_duration: float,
    bins: int = 241,
) -> dict[str, float]:
    """Estimate duration from the folded profile using half-depth crossings.

    The returned value is a morphology estimate, not a physically fitted duration.
    It is useful for detecting grossly wrong candidate durations and for reporting
    a refined first-pass estimate.
    """
    folded = phase_fold_time(time, period, t0)
    finite = np.isfinite(folded) & np.isfinite(flux)
    folded = folded[finite]
    y = np.asarray(flux, dtype=float)[finite]
    if len(folded) < 50:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}

    span = max(0.5 * period, 6.0 * initial_duration)
    span = min(span, 0.5 * period)
    m = np.abs(folded) <= span
    if m.sum() < 30:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}

    edges = np.linspace(-span, span, bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    prof = np.full(bins, np.nan)
    for i in range(bins):
        mm = (folded >= edges[i]) & (folded < edges[i + 1])
        if mm.sum() >= 3:
            prof[i] = np.nanmedian(y[mm])

    finite_prof = np.isfinite(prof)
    if finite_prof.sum() < 20:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}

    out = np.abs(centers) > max(1.5 * initial_duration, 0.1 * span)
    if out.sum() < 5:
        out = np.abs(centers) > initial_duration
    baseline = np.nanmedian(prof[out & finite_prof]) if np.any(out & finite_prof) else np.nanmedian(prof[finite_prof])
    center_region = np.abs(centers) < max(0.5 * initial_duration, (centers[1] - centers[0]) * 2)
    min_flux = np.nanmedian(prof[center_region & finite_prof]) if np.any(center_region & finite_prof) else np.nanmin(prof[finite_prof])
    depth = baseline - min_flux
    if not np.isfinite(depth) or depth <= 0:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}

    threshold = baseline - 0.5 * depth
    below = finite_prof & (prof < threshold)
    if below.sum() < 2:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}

    width = centers[below].max() - centers[below].min()
    # Guard against absurd profile widths.
    if not np.isfinite(width) or width <= 0 or width > 0.5 * period:
        return {"duration_days_profile": float(initial_duration), "half_depth_width_days": np.nan, "duration_method": "fallback_initial"}
    return {"duration_days_profile": float(width), "half_depth_width_days": float(width), "duration_method": "half_depth_profile"}


def _box_snr_for_grid(time: np.ndarray, flux: np.ndarray, period: float, t0: float, duration: float) -> float:
    in_tr = make_transit_mask(time, period, t0, duration, width_factor=1.0)
    near = make_transit_mask(time, period, t0, duration, width_factor=5.0)
    out = ~near
    if in_tr.sum() < 3 or out.sum() < 20:
        return -np.inf
    baseline = np.nanmedian(flux[out])
    depth = baseline - np.nanmedian(flux[in_tr])
    noise = robust_sigma(flux[out] - np.nanmedian(flux[out]))
    if not np.isfinite(depth) or not np.isfinite(noise) or noise <= 0:
        return -np.inf
    return float(depth / noise * np.sqrt(in_tr.sum()))


def refine_period_epoch_grid(
    time: np.ndarray,
    flux: np.ndarray,
    candidate: CandidateSignal,
    period_frac_width: float = 0.002,
    n_period: int = 25,
    n_epoch: int = 25,
) -> dict[str, float]:
    """Tiny local grid search around detected period/T0 using box SNR.

    This is a robust dependency-free refinement. It deliberately does not pretend
    to replace a full physical transit fit; it simply improves the first-pass
    ephemeris before feature extraction and plotting.
    """
    p0 = candidate.period_days
    t00 = candidate.epoch_time
    dur = candidate.duration_days
    if not np.isfinite(p0) or p0 <= 0 or not np.isfinite(t00) or not np.isfinite(dur) or dur <= 0:
        return {"period_days_refined": p0, "epoch_time_refined": t00, "refinement_snr": candidate.local_snr}

    periods = np.linspace(p0 * (1 - period_frac_width), p0 * (1 + period_frac_width), n_period)
    epochs = np.linspace(t00 - 0.5 * dur, t00 + 0.5 * dur, n_epoch)
    best = (-np.inf, p0, t00)
    for p in periods:
        for t0 in epochs:
            s = _box_snr_for_grid(time, flux, p, t0, dur)
            if s > best[0]:
                best = (s, p, t0)
    return {"period_days_refined": float(best[1]), "epoch_time_refined": float(best[2]), "refinement_snr": float(best[0])}


def bootstrap_depth_uncertainty(event_depths: pd.DataFrame, random_seed: int = 42, n_bootstrap: int = 1000) -> dict[str, float]:
    vals = np.asarray(event_depths.get("depth_fraction", []), dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return {"depth_fraction_bootstrap_err": np.nan, "depth_ppm_bootstrap_err": np.nan}
    if vals.size == 1:
        err = np.nan
    else:
        rng = np.random.default_rng(random_seed)
        boot = np.empty(n_bootstrap)
        for i in range(n_bootstrap):
            boot[i] = np.nanmedian(rng.choice(vals, size=vals.size, replace=True))
        err = float(np.nanstd(boot, ddof=1))
    return {"depth_fraction_bootstrap_err": err, "depth_ppm_bootstrap_err": err * 1e6 if np.isfinite(err) else np.nan}


def refine_candidate_parameters(
    clean: CleanLightCurve,
    candidate: CandidateSignal,
    n_bootstrap: int = 500,
) -> TransitFitResult:
    """Refine period/T0/depth/duration and estimate first-pass uncertainties."""
    time = np.asarray(clean.time, dtype=float)
    flux = np.asarray(clean.flux_detrended, dtype=float)
    finite = np.isfinite(time) & np.isfinite(flux)
    time = time[finite]
    flux = flux[finite]

    warnings: list[str] = []
    if len(time) < 50:
        warnings.append("TOO_FEW_POINTS_FOR_REFINEMENT")

    ref = refine_period_epoch_grid(time, flux, candidate)
    period = _safe_float(ref["period_days_refined"], candidate.period_days)
    t0 = _safe_float(ref["epoch_time_refined"], candidate.epoch_time)
    duration_initial = _safe_float(candidate.duration_days, np.nan)

    dur_info = estimate_duration_from_folded_profile(time, flux, period, t0, duration_initial)
    duration = _safe_float(dur_info["duration_days_profile"], duration_initial)
    if duration <= 0 or not np.isfinite(duration):
        duration = duration_initial
        warnings.append("DURATION_REFINEMENT_FAILED")

    events = estimate_event_depths(time, flux, period, t0, duration)
    good_depths = events["depth_fraction"].to_numpy(dtype=float) if "depth_fraction" in events else np.array([])
    good_depths = good_depths[np.isfinite(good_depths)]

    if good_depths.size:
        depth = float(np.nanmedian(good_depths))
        depth_event_scatter = float(robust_sigma(good_depths)) if good_depths.size > 1 else np.nan
    else:
        in_tr = make_transit_mask(time, period, t0, duration)
        out = ~make_transit_mask(time, period, t0, duration, width_factor=5.0)
        if in_tr.sum() >= 3 and out.sum() >= 20:
            depth = float(np.nanmedian(flux[out]) - np.nanmedian(flux[in_tr]))
            depth_event_scatter = np.nan
        else:
            depth = _safe_float(candidate.depth_fraction)
            depth_event_scatter = np.nan
            warnings.append("DEPTH_REFINEMENT_SPARSE")

    depth_boot = bootstrap_depth_uncertainty(events, random_seed=int(clean.qc.get("random_seed", 42)), n_bootstrap=n_bootstrap)
    in_tr = make_transit_mask(time, period, t0, duration)
    out = ~make_transit_mask(time, period, t0, duration, width_factor=5.0)
    noise = robust_sigma(flux[out] - np.nanmedian(flux[out])) if out.sum() > 20 else np.nan
    n_in = int(in_tr.sum())
    snr = depth / noise * np.sqrt(n_in) if np.isfinite(depth) and np.isfinite(noise) and noise > 0 else np.nan

    rp_over_rstar = np.sqrt(depth) if np.isfinite(depth) and depth > 0 else np.nan
    rstar = clean.metadata.get("stellar_radius") or clean.metadata.get("RADIUS") or clean.metadata.get("rad")
    try:
        rstar = float(rstar) if rstar is not None else np.nan
    except Exception:
        rstar = np.nan
    rp_earth = float(rp_over_rstar * rstar * 109.2) if np.isfinite(rp_over_rstar) and np.isfinite(rstar) and rstar > 0 else np.nan

    # Rough period uncertainty: duration divided by baseline and SNR. Conservative placeholder.
    baseline = np.nanmax(time) - np.nanmin(time) if len(time) else np.nan
    period_err = abs(period) * (duration / baseline) / max(snr, 1.0) if np.isfinite(baseline) and baseline > 0 and np.isfinite(snr) else np.nan
    epoch_err = duration / max(snr, 1.0) if np.isfinite(duration) and np.isfinite(snr) else np.nan
    duration_err = 0.25 * duration if np.isfinite(duration) else np.nan
    depth_err = depth_boot["depth_fraction_bootstrap_err"]
    if not np.isfinite(depth_err) and np.isfinite(noise) and n_in > 0:
        depth_err = noise / np.sqrt(n_in)

    return TransitFitResult(
        tic_id=clean.tic_id,
        sector=clean.sector,
        candidate_id=candidate.candidate_id,
        period_days=float(period),
        period_err_days=float(period_err),
        epoch_time=float(t0),
        epoch_err_days=float(epoch_err),
        duration_days=float(duration),
        duration_err_days=float(duration_err),
        depth_fraction=float(depth),
        depth_err_fraction=float(depth_err),
        depth_ppm=float(depth * 1e6),
        depth_err_ppm=float(depth_err * 1e6) if np.isfinite(depth_err) else np.nan,
        rp_over_rstar=float(rp_over_rstar),
        rp_earth=float(rp_earth),
        stellar_radius_rsun=float(rstar) if np.isfinite(rstar) else np.nan,
        snr=float(snr),
        n_in_transit_points=n_in,
        n_events=int(len(events)),
        n_good_events=int(good_depths.size),
        event_depth_scatter_ppm=float(depth_event_scatter * 1e6) if np.isfinite(depth_event_scatter) else np.nan,
        method="box_profile_grid_refinement",
        warnings=warnings,
        event_depths=events.to_dict(orient="records"),
        extra={**ref, **dur_info, **depth_boot},
    )


def fit_to_dataframe(fit: TransitFitResult) -> pd.DataFrame:
    d = asdict(fit)
    d.pop("event_depths", None)
    d["warnings"] = ";".join(fit.warnings)
    return pd.DataFrame([d])
