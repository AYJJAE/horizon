"""
backend/preprocessing/normalization.py
Flux normalization for light curve preprocessing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NormalizationResult:
    flux: np.ndarray
    flux_err: Optional[np.ndarray]
    median: float
    std: float
    method: str


def median_normalize(
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
) -> NormalizationResult:
    """
    Normalize flux by dividing by the median (unit median).
    Standard approach for exoplanet transit photometry.
    """
    med = float(np.nanmedian(flux))
    if med == 0:
        raise ValueError("Median flux is zero — cannot normalize.")

    norm_flux = flux / med
    norm_err = flux_err / med if flux_err is not None else None
    std = float(np.nanstd(norm_flux))

    logger.debug("Median normalization: median=%.4f, std=%.6f", med, std)
    return NormalizationResult(
        flux=norm_flux,
        flux_err=norm_err,
        median=med,
        std=std,
        method="median",
    )


def zscore_normalize(
    flux: np.ndarray,
    flux_err: Optional[np.ndarray] = None,
) -> NormalizationResult:
    """Normalize flux to zero mean and unit variance (z-score)."""
    mean = float(np.nanmean(flux))
    std = float(np.nanstd(flux))
    if std == 0:
        raise ValueError("Flux standard deviation is zero.")

    norm_flux = (flux - mean) / std
    norm_err = flux_err / std if flux_err is not None else None

    logger.debug("Z-score normalization: mean=%.4f, std=%.6f", mean, std)
    return NormalizationResult(
        flux=norm_flux,
        flux_err=norm_err,
        median=mean,
        std=std,
        method="zscore",
    )
