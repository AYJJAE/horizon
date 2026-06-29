"""
backend/transit_detection/tls_detector.py
Transit Least Squares (TLS) detection — the gold standard for exoplanet transits.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TLSResult:
    period: float            # Best-fit period (days)
    epoch: float             # First transit epoch (BJD)
    duration: float          # Transit duration (days)
    depth: float             # Transit depth (fractional, 1 - transit minimum)
    snr: float               # Signal-to-noise ratio
    sde: float               # Signal Detection Efficiency (TLS specific)
    num_transits: int
    odd_even_mismatch: float
    periodogram_periods: List[float] = field(default_factory=list)
    periodogram_power: List[float] = field(default_factory=list)
    folded_time: List[float] = field(default_factory=list)
    folded_flux: List[float] = field(default_factory=list)
    model_flux: List[float] = field(default_factory=list)
    transit_times: List[float] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


def run_tls(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
    min_period: float = 0.5,
    max_period: float = 27.0,
    snr_threshold: float = 7.0,
    stellar_params: Optional[Dict[str, float]] = None,
) -> Optional[TLSResult]:
    """
    Run Transit Least Squares search.
    Falls back to a manual BLS-like approach if TLS is not installed.
    """
    try:
        from transitleastsquares import transitleastsquares, cleaned_array
        return _run_tls_native(
            time, flux, flux_err,
            min_period, max_period, snr_threshold, stellar_params,
        )
    except ImportError:
        logger.warning("transitleastsquares not installed, using BLS fallback for TLS slot.")
        return _run_tls_fallback(time, flux, flux_err, min_period, max_period, snr_threshold)


def _run_tls_native(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray],
    min_period: float,
    max_period: float,
    snr_threshold: float,
    stellar_params: Optional[Dict[str, float]],
) -> Optional[TLSResult]:
    from transitleastsquares import transitleastsquares

    if flux_err is None:
        flux_err = np.ones_like(flux) * np.nanstd(flux) * 0.1

    kwargs: Dict[str, Any] = {
        "period_min": min_period,
        "period_max": max_period,
        "show_progress_bar": False,
    }
    if stellar_params:
        if "radius" in stellar_params:
            kwargs["R_star"] = stellar_params["radius"]
        if "mass" in stellar_params:
            kwargs["M_star"] = stellar_params["mass"]

    model = transitleastsquares(time, flux, flux_err)
    results = model.power(**kwargs)

    if results.snr < snr_threshold:
        logger.info("TLS SNR %.2f below threshold %.2f", results.snr, snr_threshold)
        return None

    tls_result = TLSResult(
        period=float(results.period),
        epoch=float(results.T0),
        duration=float(results.duration),
        depth=float(1.0 - results.depth_mean_even),
        snr=float(results.snr),
        sde=float(results.SDE),
        num_transits=int(results.transit_count),
        odd_even_mismatch=float(results.odd_even_mismatch),
        periodogram_periods=results.periods.tolist(),
        periodogram_power=results.power.tolist(),
        folded_time=results.folded_phase.tolist(),
        folded_flux=results.folded_y.tolist(),
        model_flux=results.model_folded_model.tolist(),
        transit_times=results.transit_times.tolist() if hasattr(results.transit_times, "tolist") else list(results.transit_times),
        stats={
            "sde_raw": float(results.SDE_raw),
            "chi2_min": float(results.chi2_min),
            "depth_mean": float(results.depth_mean),
            "rp_rs": float(results.rp_rs),
        },
    )
    logger.info("TLS result: period=%.4f d, SDE=%.2f, SNR=%.2f", tls_result.period, tls_result.sde, tls_result.snr)
    return tls_result


def _run_tls_fallback(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray],
    min_period: float,
    max_period: float,
    snr_threshold: float,
) -> Optional[TLSResult]:
    """Minimal BLS-based fallback when TLS library unavailable."""
    from backend.transit_detection.bls_detector import run_bls
    bls = run_bls(time, flux, flux_err, min_period, max_period, snr_threshold=snr_threshold)
    if bls is None:
        return None
    return TLSResult(
        period=bls.period,
        epoch=bls.epoch,
        duration=bls.duration,
        depth=bls.depth,
        snr=bls.snr,
        sde=bls.power,
        num_transits=bls.num_transits,
        odd_even_mismatch=bls.odd_even_mismatch,
        periodogram_periods=bls.periodogram_periods,
        periodogram_power=bls.periodogram_power,
        folded_time=bls.folded_time,
        folded_flux=bls.folded_flux,
        model_flux=bls.model_flux,
        transit_times=[],
        stats=bls.stats,
    )
