# Test Status

Verified after the latest audit in this environment.

```text
PYTHONDONTWRITEBYTECODE=1 .context/audit-venv/bin/python -m pytest -q tests --tb=short --disable-warnings
26 passed, 883 warnings
```

Additional checks completed:

- `uv pip check --python .context/audit-venv/bin/python` passed.
- `PYTHONPYCACHEPREFIX=.context/pycache .context/audit-venv/bin/python -m compileall -q src scripts tests` passed.
- All notebooks are valid JSON.
- `.context/audit-venv/bin/python scripts/run_parts_9_10_synthetic_batch.py --output-dir .context/audit_parts_9_10 --n-periods 500` completed successfully.
- The synthetic batch produced 3 targets, 3 candidates, and correctly separated planet-like, eclipsing-binary, and blend-like examples.
- The test suite now includes CLI smoke checks, generated TESS-like FITS ingestion tests, final-catalog schema validation, empty-batch output checks, and candidate-ID based uncertainty alignment.
- Generated outputs are not tracked; scripts regenerate them on demand.

Notes:

- The package is a strong submission-grade skeleton, not a planet-validation service. High-value candidates still need target-pixel-file difference imaging, Gaia nearby-source checks, and external catalog vetting.
- The default fast synthetic demos use relatively small BLS grids for speed. For real sector-scale use, increase `--n-periods`; TLS remains runtime-optional because the current `transitleastsquares` release depends on an old numba stack on modern Python.
