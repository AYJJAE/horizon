"""
backend/transit_detection/bls_detector.py
Box Least Squares transit detection using astropy.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
from astropy.timeseries import BoxLeastSquares
import astropy.units as u

logger = logging.getLogger(__name__)


@dataclass
class BLSResult:
    period: float            # Best-fit period (days)
    epoch: float             # Transit midpoint (BJD)
    duration: float          # Transit duration (days)
    depth: float             # Transit depth (fractional)
    snr: float               # Signal-to-noise ratio
    power: float             # BLS power at best period
    num_transits: int
    odd_even_mismatch: float
    periodogram_periods: List[float] = field(default_factory=list)
    periodogram_power: List[float] = field(default_factory=list)
    folded_time: List[float] = field(default_factory=list)
    folded_flux: List[float] = field(default_factory=list)
    model_flux: List[float] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


def run_bls(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
    min_period: float = 0.5,
    max_period: float = 27.0,
    duration_grid: Optional[np.ndarray] = None,
    snr_threshold: float = 7.0,
) -> Optional[BLSResult]:
    """
    Run Box Least Squares transit search.

    Returns the best-fit BLSResult or None if no significant signal found.
    """
    if flux_err is None:
        flux_err = np.ones_like(flux) * np.nanstd(flux)

    # Duration grid in hours → days
    if duration_grid is None:
        duration_grid = np.array([0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]) / 24.0

    try:
        model = BoxLeastSquares(time * u.day, flux, dy=flux_err)
        periodogram = model.autopower(
            duration_grid * u.day,
            minimum_period=min_period * u.day,
            maximum_period=max_period * u.day,
            frequency_factor=1.5,
        )
    except Exception as exc:
        logger.error("BLS computation failed: %s", exc)
        return None

    # Best period
    best_idx = np.argmax(periodogram.power)
    best_period = float(periodogram.period[best_idx].value)
    best_power = float(periodogram.power[best_idx])

    # Compute best-fit parameters
    params = model.compute_stats(
        periodogram.period[best_idx],
        periodogram.duration[best_idx],
        periodogram.transit_time[best_idx],
    )

    depth = float(params["depth"][0]) if hasattr(params["depth"], "__len__") else float(params["depth"])
    duration = float(periodogram.duration[best_idx].value)
    epoch = float(periodogram.transit_time[best_idx].value)

    # SNR estimate
    sigma_flux = float(np.nanstd(flux))
    num_transits = max(1, int((time[-1] - time[0]) / best_period))
    n_in_transit = max(1, int(duration / np.median(np.diff(time))))
    snr = abs(depth) / (sigma_flux / np.sqrt(n_in_transit * num_transits))

    if snr < snr_threshold:
        logger.info("BLS best SNR %.2f below threshold %.2f", snr, snr_threshold)
        return None

    # Fold light curve
    phase = (time - epoch) % best_period / best_period
    phase[phase > 0.5] -= 1.0
    sort_idx = np.argsort(phase)
    folded_phase = phase[sort_idx].tolist()
    folded_flux_arr = flux[sort_idx].tolist()

    # Build model
    model_time = np.linspace(0, best_period, 500)
    model_phase = (model_time / best_period) - 0.5
    in_transit = np.abs(model_phase) < (duration / best_period / 2)
    model_arr = np.where(in_transit, 1.0 - depth, 1.0).tolist()

    # Odd-even comparison
    odd_depths, even_depths = [], []
    for k in range(num_transits):
        t_center = epoch + k * best_period
        mask = np.abs(time - t_center) < duration / 2
        if np.sum(mask) < 3:
            continue
        d = 1.0 - float(np.median(flux[mask]))
        if k % 2 == 0:
            even_depths.append(d)
        else:
            odd_depths.append(d)
    odd_even = abs(np.mean(odd_depths) - np.mean(even_depths)) if odd_depths and even_depths else 0.0

    result = BLSResult(
        period=best_period,
        epoch=epoch,
        duration=duration,
        depth=depth,
        snr=snr,
        power=best_power,
        num_transits=num_transits,
        odd_even_mismatch=float(odd_even),
        periodogram_periods=periodogram.period.value.tolist(),
        periodogram_power=periodogram.power.tolist(),
        folded_time=folded_phase,
        folded_flux=folded_flux_arr,
        model_flux=model_arr,
        stats={
            "best_power": best_power,
            "depth_odd": float(np.mean(odd_depths)) if odd_depths else None,
            "depth_even": float(np.mean(even_depths)) if even_depths else None,
        },
    )
    logger.info("BLS result: period=%.4f d, depth=%.4f, SNR=%.2f", best_period, depth, snr)
    return result
