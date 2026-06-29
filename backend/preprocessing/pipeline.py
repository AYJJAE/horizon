"""
backend/preprocessing/pipeline.py
Orchestrates the full light curve preprocessing pipeline.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

import numpy as np

from backend.preprocessing.outlier_removal import remove_nans, sigma_clip_outliers
from backend.preprocessing.detrending import savgol_detrend, spline_detrend, wotan_detrend, interpolate_gaps
from backend.preprocessing.normalization import median_normalize

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    # Raw (NaN-removed) data
    raw_time: np.ndarray
    raw_flux: np.ndarray
    raw_flux_err: Optional[np.ndarray]

    # Cleaned data ready for transit detection
    clean_time: np.ndarray
    clean_flux: np.ndarray
    clean_flux_err: Optional[np.ndarray]

    # Trend estimated during detrending
    trend: np.ndarray

    # Statistics
    outliers_removed: int
    gaps_interpolated: int
    detrend_method: str
    summary: Dict[str, Any] = field(default_factory=dict)


class PreprocessingPipeline:
    """
    Full preprocessing pipeline for a TESS / custom light curve.

    Steps:
      1. Remove NaN / Inf
      2. Sigma-clip outliers
      3. Detrend (remove stellar variability)
      4. Interpolate gaps
      5. Median-normalize to unit median
    """

    def __init__(
        self,
        sigma_clip_sigma: float = 4.0,
        detrend_method: str = "savgol",
        savgol_window: int = 51,
        interpolate: bool = True,
        normalize: bool = True,
    ) -> None:
        self.sigma_clip_sigma = sigma_clip_sigma
        self.detrend_method = detrend_method
        self.savgol_window = savgol_window
        self.interpolate = interpolate
        self.normalize = normalize

    def run(
        self,
        time: np.ndarray,
        flux: np.ndarray,
        flux_err: Optional[np.ndarray] = None,
    ) -> PipelineResult:
        """Execute the full pipeline and return a PipelineResult."""
        logger.info("Pipeline start: %d raw points", len(time))

        # ── Step 1: Remove NaN / Inf ─────────────────────────────────────────
        time, flux, flux_err, nan_removed = remove_nans(time, flux, flux_err)
        raw_time = time.copy()
        raw_flux = flux.copy()
        raw_flux_err = flux_err.copy() if flux_err is not None else None
        logger.debug("Step 1 (NaN removal): removed %d", nan_removed)

        # ── Step 2: Sigma-clip outliers ──────────────────────────────────────
        clip_result = sigma_clip_outliers(time, flux, flux_err, sigma=self.sigma_clip_sigma)
        time = clip_result.time
        flux = clip_result.flux
        flux_err = clip_result.flux_err
        outliers_removed = clip_result.num_removed + nan_removed
        logger.debug("Step 2 (outliers): removed %d total", outliers_removed)

        # ── Step 3: Detrend ──────────────────────────────────────────────────
        if self.detrend_method == "spline":
            detrend_result = spline_detrend(time, flux)
        elif self.detrend_method == "wotan":
            detrend_result = wotan_detrend(time, flux)
        else:  # savgol (default)
            detrend_result = savgol_detrend(time, flux, window_length=self.savgol_window)

        trend = detrend_result.trend
        flux = detrend_result.flux
        logger.debug("Step 3 (detrend): method=%s", detrend_result.method)

        # ── Step 4: Interpolate gaps ─────────────────────────────────────────
        gaps_interpolated = 0
        if self.interpolate:
            time, flux, flux_err, gaps_interpolated = interpolate_gaps(time, flux, flux_err)
            # Re-align trend to new time array
            trend = np.interp(time, detrend_result.time, trend)
            logger.debug("Step 4 (gaps): interpolated %d points", gaps_interpolated)

        # ── Step 5: Normalize ────────────────────────────────────────────────
        if self.normalize:
            norm_result = median_normalize(flux, flux_err)
            flux = norm_result.flux
            flux_err = norm_result.flux_err
            trend_med = float(np.nanmedian(raw_flux))
            if trend_med != 0:
                trend = trend / trend_med
            logger.debug("Step 5 (normalize): median=%.4f", norm_result.median)

        summary = {
            "raw_points": len(raw_time),
            "clean_points": len(time),
            "outliers_removed": outliers_removed,
            "gaps_interpolated": gaps_interpolated,
            "detrend_method": self.detrend_method,
            "flux_mean": float(np.nanmean(flux)),
            "flux_std": float(np.nanstd(flux)),
            "time_span_days": float(time[-1] - time[0]) if len(time) > 1 else 0.0,
        }

        logger.info("Pipeline complete: %d clean points, %d outliers removed", len(time), outliers_removed)

        return PipelineResult(
            raw_time=raw_time,
            raw_flux=raw_flux,
            raw_flux_err=raw_flux_err,
            clean_time=time,
            clean_flux=flux,
            clean_flux_err=flux_err,
            trend=trend,
            outliers_removed=outliers_removed,
            gaps_interpolated=gaps_interpolated,
            detrend_method=self.detrend_method,
            summary=summary,
        )
