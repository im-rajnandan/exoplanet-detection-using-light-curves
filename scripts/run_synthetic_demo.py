from pathlib import Path

from exoplanet_pipeline.config import PipelineConfig
from exoplanet_pipeline.synthetic import make_synthetic_transit_lc
from exoplanet_pipeline.preprocess import preprocess_raw_lightcurve, save_clean_lightcurve
from exoplanet_pipeline.detect import detect_candidates, candidates_to_dataframe
from exoplanet_pipeline.diagnostics import plot_preprocessing, plot_detection


def main():
    cfg = PipelineConfig(detection_method="bls", n_periods=3000)
    raw = make_synthetic_transit_lc(period_days=3.0, depth_ppm=1000, duration_hours=2.0, noise_ppm=300)
    clean = preprocess_raw_lightcurve(raw, cfg)
    save_clean_lightcurve(clean, "data/processed")
    plot_preprocessing(clean, "plots/preprocessing/synthetic_preprocessing.png")
    result = detect_candidates(clean, cfg)
    plot_detection(clean, result, "plots/detection/synthetic_detection.png")
    df = candidates_to_dataframe(result)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/processed/synthetic_candidates.csv", index=False)
    print(df[["period_days", "duration_days", "depth_ppm", "local_snr", "status"]].head())


if __name__ == "__main__":
    main()
