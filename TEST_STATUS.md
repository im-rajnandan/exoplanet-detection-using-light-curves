# Test Status

Verified after the final audit in this environment.

```text
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests --tb=short --disable-warnings
17 passed in 23.31s
```

Additional checks completed:

- `python -m compileall -q src scripts tests` passed.
- All notebooks are valid JSON and contain cells.
- `scripts/run_parts_9_10_synthetic_batch.py --output-dir /mnt/data/audit_run2 --n-periods 500` completed successfully.
- The synthetic batch produced 3 targets, 3 candidates, and correctly separated planet-like, eclipsing-binary, and blend-like examples.
- Resume logic was tested for a zero-candidate/no-signal target.

Notes:

- The package is a strong submission-grade skeleton, not a planet-validation service. High-value candidates still need target-pixel-file difference imaging, Gaia nearby-source checks, and external catalog vetting.
- The default fast synthetic demos use relatively small BLS grids for speed. For real sector-scale use, increase `--n-periods` and consider TLS where runtime allows.
