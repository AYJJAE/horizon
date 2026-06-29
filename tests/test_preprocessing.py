"""
tests/test_preprocessing.py
Unit tests for the preprocessing pipeline.
"""
import numpy as np
import pytest

from backend.preprocessing.pipeline import PreprocessingPipeline
from backend.preprocessing.outlier_removal import sigma_clip_outliers, remove_nans
from backend.preprocessing.detrending import savgol_detrend, spline_detrend
from backend.preprocessing.normalization import median_normalize


def make_lc(n=1000, noise=0.001, trend_amplitude=0.05, seed=42):
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 27, n)
    trend = 1.0 + trend_amplitude * np.sin(2 * np.pi * time / 10)
    flux = trend + rng.normal(0, noise, n)
    # Inject a few outliers
    flux[100] = 1.5
    flux[200] = 0.5
    return time, flux


def test_remove_nans():
    time = np.array([1.0, np.nan, 3.0, 4.0, np.inf])
    flux = np.array([1.0, 1.0, np.nan, 1.0, 1.0])
    t, f, e, n = remove_nans(time, flux)
    assert len(t) == 2
    assert n == 3
    assert np.all(np.isfinite(t))


def test_sigma_clip_removes_outliers():
    time, flux = make_lc(n=500)
    result = sigma_clip_outliers(time, flux, sigma=4.0)
    assert result.num_removed >= 2  # The two injected outliers
    assert len(result.flux) < 500


def test_savgol_detrend():
    time, flux = make_lc(n=500)
    result = savgol_detrend(time, flux, window_length=51)
    assert len(result.flux) == len(time)
    assert result.method == "savgol"
    # Detrended flux should be centered near 1.0 (median normalized)
    assert 0.95 < np.median(result.flux) < 1.05


def test_spline_detrend():
    time, flux = make_lc(n=500)
    result = spline_detrend(time, flux, n_knots=10)
    assert len(result.flux) == len(time)


def test_median_normalize():
    flux = np.array([100.0, 100.0, 100.0, 90.0])  # one dip
    result = median_normalize(flux)
    assert abs(np.median(result.flux) - 1.0) < 0.01


def test_full_pipeline():
    time, flux = make_lc(n=1000)
    pipeline = PreprocessingPipeline(sigma_clip_sigma=4.0, detrend_method="savgol", normalize=True, interpolate=True)
    result = pipeline.run(time, flux)
    assert result.outliers_removed >= 2
    assert len(result.clean_flux) > 0
    assert abs(np.median(result.clean_flux) - 1.0) < 0.02
    assert result.summary["clean_points"] <= result.summary["raw_points"]


def test_pipeline_with_gaps():
    rng = np.random.default_rng(0)
    time = np.concatenate([np.linspace(0, 10, 500), np.linspace(12, 27, 700)])  # gap at 10-12
    flux = 1.0 + rng.normal(0, 0.001, len(time))
    pipeline = PreprocessingPipeline(interpolate=True)
    result = pipeline.run(time, flux)
    assert result.gaps_interpolated > 0
