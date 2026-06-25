import argparse
from pathlib import Path

from exoplanet_pipeline.config import PipelineConfig
from exoplanet_pipeline.preprocess import preprocess_fits_file, save_clean_lightcurve
from exoplanet_pipeline.detect import detect_candidates, candidates_to_dataframe
from exoplanet_pipeline.diagnostics import plot_preprocessing, plot_detection


def main():
    parser = argparse.ArgumentParser(description="Preprocess one TESS FITS light curve and detect periodic dips.")
    parser.add_argument("fits_file", help="Path to local TESS light-curve FITS file")
    parser.add_argument("--method", choices=["bls", "tls", "both"], default="bls")
    parser.add_argument("--period-min", type=float, default=0.2)
    parser.add_argument("--period-max", type=float, default=None)
    parser.add_argument("--n-periods", type=int, default=4000)
    args = parser.parse_args()

    cfg = PipelineConfig(
        detection_method=args.method,
        period_min_days=args.period_min,
        period_max_days=args.period_max,
        n_periods=args.n_periods,
    )
    clean = preprocess_fits_file(args.fits_file, cfg)
    stem = f"TIC_{clean.tic_id or 'unknown'}_S{clean.sector or 'unknown'}"
    save_clean_lightcurve(clean, "data/processed")
    plot_preprocessing(clean, f"plots/preprocessing/{stem}_preprocessing.png")

    result = detect_candidates(clean, cfg)
    plot_detection(clean, result, f"plots/detection/{stem}_detection.png")
    df = candidates_to_dataframe(result)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv(f"data/processed/{stem}_candidates.csv", index=False)
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
