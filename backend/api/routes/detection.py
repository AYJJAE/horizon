"""
backend/api/routes/detection.py
Transit detection endpoints: run TLS and/or BLS on a dataset.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.models.orm import Dataset, ProcessingJob, TransitCandidate
from backend.models.schemas import DetectionConfig, DetectionResult, TransitCandidateOut
from backend.preprocessing.pipeline import PreprocessingPipeline
from backend.api.routes.preprocessing import _load_light_curve
from backend.transit_detection.bls_detector import run_bls
from backend.transit_detection.tls_detector import run_tls

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/detection", tags=["Transit Detection"])


@router.post("/{dataset_id}", response_model=DetectionResult, summary="Run transit detection (TLS+BLS)")
async def run_detection(
    dataset_id: str,
    config: Optional[DetectionConfig] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Run TLS and/or BLS transit detection on a preprocessed dataset.
    Detected candidates are stored in the database and returned.
    """
    config = config or DetectionConfig()

    result_row = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result_row.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    job = ProcessingJob(
        id=str(uuid.uuid4()),
        dataset_id=dataset_id,
        job_type="detection",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()

    try:
        time, flux, flux_err = await _load_light_curve(dataset)

        # Quick preprocessing (sigma-clip + detrend) if not already done
        pipeline = PreprocessingPipeline(normalize=True, interpolate=True)
        pp = pipeline.run(time, flux, flux_err)
        c_time = pp.clean_time
        c_flux = pp.clean_flux
        c_err = pp.clean_flux_err

        stellar_params = None
        if dataset.stellar_radius or dataset.stellar_mass:
            stellar_params = {
                "radius": dataset.stellar_radius or 1.0,
                "mass": dataset.stellar_mass or 1.0,
            }

        candidates_created = []
        periodogram_data = None

        # ── TLS ──────────────────────────────────────────────────────────────
        if config.method in ("tls", "both"):
            job.progress = 20
            await db.commit()
            tls_result = run_tls(
                c_time, c_flux, c_err,
                min_period=config.min_period,
                max_period=config.max_period,
                snr_threshold=config.snr_threshold,
                stellar_params=stellar_params,
            )
            if tls_result:
                cand = TransitCandidate(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset_id,
                    method="TLS",
                    period=tls_result.period,
                    epoch=tls_result.epoch,
                    duration=tls_result.duration,
                    depth=tls_result.depth,
                    snr=tls_result.snr,
                    sde=tls_result.sde,
                    num_transits=tls_result.num_transits,
                    odd_even_mismatch=tls_result.odd_even_mismatch,
                    transit_data={
                        "folded_time": tls_result.folded_time[:2000],
                        "folded_flux": tls_result.folded_flux[:2000],
                        "model_flux": tls_result.model_flux[:500],
                        "transit_times": tls_result.transit_times,
                        "periodogram_periods": tls_result.periodogram_periods[:1000],
                        "periodogram_power": tls_result.periodogram_power[:1000],
                        "stats": tls_result.stats,
                    },
                )
                db.add(cand)
                candidates_created.append(cand)
                if not periodogram_data:
                    periodogram_data = {
                        "periods": tls_result.periodogram_periods[:1000],
                        "power": tls_result.periodogram_power[:1000],
                        "best_period": tls_result.period,
                        "method": "TLS",
                    }

        # ── BLS ──────────────────────────────────────────────────────────────
        if config.method in ("bls", "both"):
            job.progress = 60
            await db.commit()
            bls_result = run_bls(
                c_time, c_flux, c_err,
                min_period=config.min_period,
                max_period=config.max_period,
                snr_threshold=config.snr_threshold,
            )
            if bls_result:
                cand = TransitCandidate(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset_id,
                    method="BLS",
                    period=bls_result.period,
                    epoch=bls_result.epoch,
                    duration=bls_result.duration,
                    depth=bls_result.depth,
                    snr=bls_result.snr,
                    sde=bls_result.power,
                    num_transits=bls_result.num_transits,
                    odd_even_mismatch=bls_result.odd_even_mismatch,
                    transit_data={
                        "folded_time": bls_result.folded_time[:2000],
                        "folded_flux": bls_result.folded_flux[:2000],
                        "model_flux": bls_result.model_flux[:500],
                        "transit_times": [],
                        "periodogram_periods": bls_result.periodogram_periods[:1000],
                        "periodogram_power": bls_result.periodogram_power[:1000],
                        "stats": bls_result.stats,
                    },
                )
                db.add(cand)
                candidates_created.append(cand)
                if not periodogram_data:
                    periodogram_data = {
                        "periods": bls_result.periodogram_periods[:1000],
                        "power": bls_result.periodogram_power[:1000],
                        "best_period": bls_result.period,
                        "method": "BLS",
                    }

        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        job.result = {"num_candidates": len(candidates_created)}
        await db.commit()

        for c in candidates_created:
            await db.refresh(c)

        return DetectionResult(
            dataset_id=dataset_id,
            job_id=job.id,
            num_candidates=len(candidates_created),
            candidates=[TransitCandidateOut.model_validate(c) for c in candidates_created],
            periodogram=periodogram_data,
        )

    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)
        job.completed_at = datetime.utcnow()
        await db.commit()
        logger.error("Detection failed for %s: %s", dataset_id, exc)
        raise HTTPException(500, f"Detection failed: {exc}")


@router.get("/{dataset_id}/candidates", summary="List all transit candidates for a dataset")
async def list_candidates(dataset_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TransitCandidate).where(TransitCandidate.dataset_id == dataset_id)
    )
    return [TransitCandidateOut.model_validate(c) for c in result.scalars().all()]
