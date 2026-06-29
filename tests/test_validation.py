"""
tests/test_validation.py
Unit tests for statistical and ML validation.
"""
import numpy as np
import pytest

from backend.candidate_validation.statistical_validator import validate_candidate
from backend.candidate_validation.false_positive import classify_false_positive
from backend.characterization.planet_params import estimate_planet_params


def make_planet_lc(period=3.5, depth=0.01, duration=0.1, n=5000, noise=0.001, seed=42):
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 27, n)
    flux = np.ones(n)
    epoch = 1.0
    for k in range(int(27 / period) + 1):
        tc = epoch + k * period
        mask = np.abs(time - tc) < duration / 2
        flux[mask] = 1.0 - depth
    flux += rng.normal(0, noise, n)
    return time, flux


def test_statistical_validator_planet_passes():
    time, flux = make_planet_lc(period=5.0, depth=0.012, duration=0.12)
    result = validate_candidate(time, flux, period=5.0, epoch=1.0, duration=0.12, depth=0.012, snr=15.0)
    assert result.score > 0.3  # Should pass most tests
    assert not result.snr_flag


def test_statistical_validator_low_snr_flag():
    time, flux = make_planet_lc()
    result = validate_candidate(time, flux, period=5.0, epoch=1.0, duration=0.12, depth=0.012, snr=4.0)
    assert result.snr_flag is True


def test_fp_classifier_planet():
    fp = classify_false_positive(
        ml_confidence=0.85, ml_label="PLANET",
        statistical_score=0.9,
        odd_even_flag=False, shape_flag=False, depth_stability_flag=False,
        snr=15.0, depth=0.01, period=5.0, duration=0.12,
    )
    assert fp.category == "planet_candidate"
    assert fp.composite_score > 0.5


def test_fp_classifier_eclipsing_binary():
    fp = classify_false_positive(
        ml_confidence=0.2, ml_label="FALSE_POSITIVE",
        statistical_score=0.3,
        odd_even_flag=True, shape_flag=False, depth_stability_flag=False,
        snr=20.0, depth=0.05, period=3.0, duration=0.2,
    )
    assert fp.category == "eclipsing_binary"


def test_planet_params_radius():
    params = estimate_planet_params(
        candidate_id="test",
        period_days=3.5,
        depth=0.01,    # 1% transit depth → ~1 Rjup around Sun
        duration_days=0.1,
        stellar_radius_rsun=1.0,
        stellar_mass_msun=1.0,
        stellar_teff_k=5778.0,
    )
    assert params.planet_radius_rearth is not None
    assert params.planet_radius_rearth > 0
    assert params.semi_major_axis_au is not None
    assert params.semi_major_axis_au > 0
    assert params.equilibrium_temp_k is not None
    assert params.classification is not None


def test_planet_params_earth_like():
    # ~1% depth → ~10 Re, ~3.5d period
    params = estimate_planet_params("test2", 3.5, 0.0001, 0.1)  # 0.01% depth → tiny planet
    assert params.planet_radius_rearth < 3.0
