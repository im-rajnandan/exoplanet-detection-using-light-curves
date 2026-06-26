from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run_script(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_main_scripts_show_help():
    scripts = [
        "scripts/run_parts_1_to_5_fits.py",
        "scripts/run_parts_9_10_fits_directory.py",
        "scripts/train_ai_classifier_from_catalog.py",
        "scripts/validate_candidate_catalog.py",
    ]
    for script in scripts:
        result = _run_script(script, "--help")
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout.lower()


def test_fits_directory_cli_fails_fast_on_empty_directory(tmp_path: Path):
    result = _run_script("scripts/run_parts_9_10_fits_directory.py", str(tmp_path))
    assert result.returncode == 2
    assert "No FITS files found" in result.stderr
