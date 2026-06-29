"""
backend/api/routes/preprocessing.py
Preprocessing endpoint: clean + detrend a dataset's light curve.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

import numpy as np
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.models.orm import Dataset, ProcessingJob
from backend.models.schemas import PreprocessingConfig, PreprocessingResult
from backend.preprocessing.pipeline import PreprocessingPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/preprocessing", tags=["Preprocessing"])


async def _load_light_curve(dataset: Dataset):
    """Load time/flux arrays from a dataset file."""
    import pandas as pd
    from astropy.io import fits

    ftype = (dataset.file_type or "").lower()
    fpath = dataset.file_path

    if ftype in ("fits", "fit"):
        with fits.open(fpath) as hdul:
            for ext in hdul[1:]:
                if hasattr(ext, "columns") and "TIME" in ext.columns.names:
                    data = ext.data
                    time = data["TIME"].astype(float)
                    flux_col = "PDCSAP_FLUX" if "PDCSAP_FLUX" in data.names else "SAP_FLUX"
                    flux = data[flux_col].astype(float)
                    err_col = flux_col + "_ERR"
                    flux_err = data[err_col].astype(float) if err_col in data.names else None
                    return time, flux, flux_err
    else:
        df = pd.read_csv(fpath)
        tc = next((c for c in ["time", "t", "bjd"] if c in df.columns), df.columns[0])
        fc = next((c for c in ["flux", "pdcsap_flux", "sap_flux"] if c in df.columns), df.columns[1])
        ec = next((c for c in ["flux_err", "pdcsap_flux_err"] if c in df.columns), None)
        time = df[tc].values.astype(float)
        flux = df[fc].values.astype(float)
        flux_err = df[ec].values.astype(float) if ec else None
        return time, flux, flux_err

    raise ValueError(f"Could not parse light curve from {fpath}")


@router.post("/{dataset_id}", response_model=PreprocessingResult, summary="Run preprocessing pipeline")
async def run_preprocessing(
    dataset_id: str,
    config: Optional[PreprocessingConfig] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Run the full preprocessing pipeline on a dataset.
    Returns raw and cleaned arrays plus summary statistics.
    """
    config = config or PreprocessingConfig()

    result_row = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result_row.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")
    if not dataset.file_path:
        raise HTTPException(400, "Dataset has no associated file.")

    # Create processing job
    job = ProcessingJob(
        id=str(uuid.uuid4()),
        dataset_id=dataset_id,
        job_type="preprocessing",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()

    try:
        time, flux, flux_err = await _load_light_curve(dataset)

        pipeline = PreprocessingPipeline(
            sigma_clip_sigma=config.sigma_clip,
            detrend_method=config.detrend_method,
            savgol_window=config.savgol_window,
            interpolate=config.interpolate,
            normalize=config.normalize,
        )
        result = pipeline.run(time, flux, flux_err)

        # Update job
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        job.result = result.summary
        await db.commit()

        # Downsample for response (max 10k points)
        MAX_RESP = 10000

        def _downsample(arr: np.ndarray, n: int) -> list:
            if len(arr) <= n:
                return arr.tolist()
            idx = np.round(np.linspace(0, len(arr) - 1, n)).astype(int)
            return arr[idx].tolist()

        return PreprocessingResult(
            dataset_id=dataset_id,
            job_id=job.id,
            raw_time=_downsample(result.raw_time, MAX_RESP),
            raw_flux=_downsample(result.raw_flux, MAX_RESP),
            clean_time=_downsample(result.clean_time, MAX_RESP),
            clean_flux=_downsample(result.clean_flux, MAX_RESP),
            detrended_flux=_downsample(result.clean_flux, MAX_RESP),
            trend=_downsample(result.trend, min(MAX_RESP, len(result.trend))),
            outliers_removed=result.outliers_removed,
            gaps_interpolated=result.gaps_interpolated,
            summary=result.summary,
        )

    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        job.completed_at = datetime.utcnow()
        await db.commit()
        logger.error("Preprocessing failed for %s: %s", dataset_id, exc)
        raise HTTPException(500, f"Preprocessing failed: {exc}")
