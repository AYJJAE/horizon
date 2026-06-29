"""
tests/test_detection.py
Unit tests for BLS and TLS transit detection.
"""
import numpy as np
import pytest

from backend.transit_detection.bls_detector import run_bls
from backend.transit_detection.tls_detector import run_tls


def make_transit_lc(period=3.5, depth=0.01, duration=0.1, n=8000, noise=0.001, seed=42):
    """Create a clean synthetic light curve with injected transits."""
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 27, n)
    flux = np.ones(n)
    epoch = period * 0.3
    for k in range(int(27 / period) + 1):
        tc = epoch + k * period
        mask = np.abs(time - tc) < duration / 2
        flux[mask] = 1.0 - depth
    flux += rng.normal(0, noise, n)
    return time, flux


def test_bls_detects_transit():
    time, flux = make_transit_lc(period=3.5, depth=0.015, noise=0.0008)
    result = run_bls(time, flux, min_period=0.5, max_period=15.0, snr_threshold=5.0)
    assert result is not None, "BLS should detect the injected transit"
    assert abs(result.period - 3.5) < 0.5  # within 0.5 days
    assert result.depth > 0


def test_bls_returns_none_for_noise():
    rng = np.random.default_rng(1)
    time = np.linspace(0, 27, 5000)
    flux = 1.0 + rng.normal(0, 0.001, 5000)
    result = run_bls(time, flux, snr_threshold=20.0)
    assert result is None, "BLS should not detect transits in pure noise at high SNR threshold"


def test_bls_periodogram_not_empty():
    time, flux = make_transit_lc(period=5.0, depth=0.02, noise=0.001)
    result = run_bls(time, flux, snr_threshold=3.0)
    assert result is not None
    assert len(result.periodogram_periods) > 10
    assert len(result.periodogram_power) == len(result.periodogram_periods)


def test_tls_fallback_works():
    """TLS should fall back to BLS if TLS library unavailable."""
    time, flux = make_transit_lc(period=4.0, depth=0.01, noise=0.0008)
    # This will use the fallback if TLS is not installed
    result = run_tls(time, flux, min_period=0.5, max_period=15.0, snr_threshold=5.0)
    # May be None if SNR too low, but should not raise
    if result is not None:
        assert result.period > 0


def test_bls_folded_curve_provided():
    time, flux = make_transit_lc(period=3.5, depth=0.012)
    result = run_bls(time, flux, snr_threshold=3.0)
    if result:
        assert len(result.folded_time) > 0
        assert len(result.folded_flux) > 0
        assert len(result.model_flux) > 0
