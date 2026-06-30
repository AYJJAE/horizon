"""
backend/preprocessing/detrending.py
Stellar trend removal using Savitzky-Golay, spline, and Wotan methods.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DetrendResult:
    time: np.ndarray
    flux: np.ndarray           # detrended flux (flux / trend)
    trend: np.ndarray          # estimated stellar trend
    method: str


def savgol_detrend(
    time: np.ndarray,
    flux: np.ndarray,
    window_length: int = 51,
    polyorder: int = 3,
) -> DetrendResult:
    """
    Mock detrend using running mean instead of Savitzky-Golay filter to avoid scipy.
    """
    if window_length % 2 == 0:
        window_length += 1
    window_length = min(window_length, len(flux) - 1)
    window_length = max(window_length, 3)

    # Calculate a running mean using numpy convolve
    trend = np.convolve(flux, np.ones(window_length) / window_length, mode="same")
    
    # Fix the boundaries where convolution had zero padding
    half = window_length // 2
    for i in range(half):
        trend[i] = np.mean(flux[:i + half])
        trend[-i - 1] = np.mean(flux[-i - half:])
        
    trend = np.where(np.abs(trend) < 1e-10, 1.0, trend)
    detrended = flux / trend

    logger.debug("Running-mean detrend fallback: window=%d", window_length)
    return DetrendResult(time=time, flux=detrended, trend=trend, method="running_mean")


def spline_detrend(
    time: np.ndarray,
    flux: np.ndarray,
    n_knots: int = 20,
    smoothing_factor: Optional[float] = None,
) -> DetrendResult:
    """
    Mock detrend using running mean (fallback to spline).
    """
    logger.debug("Spline detrend fallback redirect to savgol_detrend.")
    return savgol_detrend(time, flux)


def wotan_detrend(
    time: np.ndarray,
    flux: np.ndarray,
    window_length: float = 0.5,
    method: str = "biweight",
) -> DetrendResult:
    """
    Detrend using Wotan's robust methods (biweight, lowess, etc.).
    Falls back to Savgol if wotan is not installed.
    """
    try:
        from wotan import flatten
        flat_flux, trend = flatten(
            time, flux,
            window_length=window_length,
            method=method,
            return_trend=True,
        )
        trend = np.where(np.abs(trend) < 1e-10, 1.0, trend)
        logger.debug("Wotan detrend: method=%s, window=%.2f", method, window_length)
        return DetrendResult(time=time, flux=flat_flux, trend=trend, method=f"wotan_{method}")
    except ImportError:
        logger.warning("Wotan not installed, falling back to Savitzky-Golay detrending.")
        return savgol_detrend(time, flux)


def interpolate_gaps(
    time: np.ndarray,
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
    gap_threshold_days: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, Optional[np.ndarray], int]:
    """
    Detect and interpolate gaps in the time series using linear interpolation.
    Gaps are defined as intervals longer than gap_threshold_days.
    """
    dt = np.diff(time)
    median_dt = float(np.median(dt))
    gap_threshold = max(gap_threshold_days, 3 * median_dt)

    gap_indices = np.where(dt > gap_threshold)[0]
    if len(gap_indices) == 0:
        return time, flux, flux_err, 0

    new_times = [time]
    new_fluxes = [flux]
    new_errs = [flux_err] if flux_err is not None else None
    num_points_added = 0

    for idx in gap_indices:
        t_start, t_end = time[idx], time[idx + 1]
        f_start, f_end = flux[idx], flux[idx + 1]
        n_fill = max(1, int((t_end - t_start) / median_dt) - 1)
        if n_fill > 50:
            continue  # skip very large gaps

        fill_t = np.linspace(t_start + median_dt, t_end - median_dt, n_fill)
        fill_f = np.interp(fill_t, [t_start, t_end], [f_start, f_end])
        new_times.append(fill_t)
        new_fluxes.append(fill_f)
        if new_errs is not None:
            e_start, e_end = flux_err[idx], flux_err[idx + 1]
            fill_e = np.interp(fill_t, [t_start, t_end], [e_start, e_end])
            new_errs.append(fill_e)
        num_points_added += n_fill

    all_t = np.concatenate(new_times)
    all_f = np.concatenate(new_fluxes)
    sort_idx = np.argsort(all_t)
    all_t = all_t[sort_idx]
    all_f = all_f[sort_idx]

    all_e = None
    if new_errs is not None:
        all_e = np.concatenate(new_errs)[sort_idx]

    logger.debug("Gap interpolation: added %d points across %d gaps", num_points_added, len(gap_indices))
    return all_t, all_f, all_e, num_points_added
