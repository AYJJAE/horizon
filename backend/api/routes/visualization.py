"""
backend/api/routes/visualization.py
Visualization data endpoints — returns Plotly.js-ready JSON plot configs.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.models.orm import Dataset, TransitCandidate
from backend.models.schemas import PlotDataResponse
from backend.visualization.plot_generator import (
    build_light_curve_plot,
    build_overlay_plot,
    build_periodogram_plot,
    build_folded_transit_plot,
    build_detection_timeline,
    build_depth_bar_chart,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/visualization", tags=["Visualization"])


@router.get("/{dataset_id}", response_model=PlotDataResponse, summary="Get all visualization data for a dataset")
async def get_visualization_data(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return all plot configurations for a dataset (raw LC, cleaned LC, periodogram, folded transit)."""
    ds_result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = ds_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    # Fetch candidates
    cand_result = await db.execute(
        select(TransitCandidate).where(TransitCandidate.dataset_id == dataset_id)
    )
    candidates = cand_result.scalars().all()

    # Load preview data
    try:
        from backend.api.routes.preprocessing import _load_light_curve
        import numpy as np
        time, flux, flux_err = await _load_light_curve(dataset)
        mask = np.isfinite(time) & np.isfinite(flux)
        time, flux = time[mask], flux[mask]

        # Downsample
        MAX_PLOT = 8000
        if len(time) > MAX_PLOT:
            idx = np.round(np.linspace(0, len(time) - 1, MAX_PLOT)).astype(int)
            t_plot, f_plot = time[idx].tolist(), flux[idx].tolist()
        else:
            t_plot, f_plot = time.tolist(), flux.tolist()

        raw_lc = build_light_curve_plot(t_plot, f_plot, title="Raw Light Curve", color="#94A3B8")
    except Exception as exc:
        logger.warning("Could not load light curve for viz: %s", exc)
        raw_lc = None

    # Periodogram from first candidate
    periodogram = None
    folded = None
    timeline = None
    depth_chart = None

    if candidates:
        best = candidates[0]
        td = best.transit_data or {}

        if td.get("periodogram_periods") and td.get("periodogram_power"):
            periodogram = build_periodogram_plot(
                periods=td["periodogram_periods"],
                power=td["periodogram_power"],
                best_period=best.period,
                method=best.method,
            )

        if td.get("folded_time") and td.get("folded_flux"):
            folded = build_folded_transit_plot(
                folded_phase=td["folded_time"],
                folded_flux=td["folded_flux"],
                model_flux=td.get("model_flux"),
                period=best.period,
                depth=best.depth,
            )

        if raw_lc and td.get("transit_times"):
            timeline = build_detection_timeline(
                time=t_plot,
                flux=f_plot,
                transit_times=td["transit_times"],
                duration=best.duration or 0.1,
            )

        # Depth bar chart across all candidates
        if len(candidates) > 1:
            depth_chart = build_depth_bar_chart(
                candidate_ids=[f"{c.method}_{i+1}" for i, c in enumerate(candidates)],
                depths_ppm=[(c.depth or 0) * 1e6 for c in candidates],
                snrs=[c.snr or 0 for c in candidates],
            )

    return PlotDataResponse(
        dataset_id=dataset_id,
        raw_light_curve=raw_lc,
        clean_light_curve=raw_lc,  # Reuse for demo; use cleaned data when available
        periodogram=periodogram,
        folded_transit=folded,
        transit_depth_chart=depth_chart,
        detection_timeline=timeline,
    )
