"""
backend/api/routes/validation.py
Candidate validation endpoint: statistical + ML scoring.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.models.orm import Dataset, TransitCandidate, ValidationResult
from backend.models.schemas import ValidationOut
from backend.candidate_validation.statistical_validator import validate_candidate
from backend.candidate_validation.ml_classifier import get_classifier
from backend.candidate_validation.false_positive import classify_false_positive
from backend.api.routes.preprocessing import _load_light_curve

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/validation", tags=["Candidate Validation"])


@router.post("/{candidate_id}", response_model=ValidationOut, summary="Validate a transit candidate")
async def validate_transit_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Run ML + statistical validation on a transit candidate.
    Returns confidence score, ML label, false-positive classification.
    """
    cand_result = await db.execute(select(TransitCandidate).where(TransitCandidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(404, "Candidate not found.")

    ds_result = await db.execute(select(Dataset).where(Dataset.id == candidate.dataset_id))
    dataset = ds_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Parent dataset not found.")

    try:
        time, flux, flux_err = await _load_light_curve(dataset)
        from backend.preprocessing.pipeline import PreprocessingPipeline
        pp = PreprocessingPipeline(normalize=True).run(time, flux, flux_err)
        c_time, c_flux = pp.clean_time, pp.clean_flux

        # ── Statistical Validation ────────────────────────────────────────────
        stat_val = validate_candidate(
            time=c_time,
            flux=c_flux,
            period=candidate.period or 1.0,
            epoch=candidate.epoch or c_time[0],
            duration=candidate.duration or 0.1,
            depth=candidate.depth or 0.001,
            snr=candidate.snr or 0.0,
        )

        # ── ML Classification ─────────────────────────────────────────────────
        transit_data = candidate.transit_data or {}
        folded_time = np.array(transit_data.get("folded_time", []))
        folded_flux = np.array(transit_data.get("folded_flux", []))

        if len(folded_time) >= 10 and len(folded_flux) >= 10:
            classifier = get_classifier()
            ml_pred = classifier.predict(folded_time, folded_flux)
            ml_confidence = ml_pred.confidence
            ml_label = ml_pred.label
            shap_values = ml_pred.shap_values
        else:
            ml_confidence = 0.5
            ml_label = "UNKNOWN"
            shap_values = None

        # ── False Positive Classification ─────────────────────────────────────
        fp_class = classify_false_positive(
            ml_confidence=ml_confidence,
            ml_label=ml_label,
            statistical_score=stat_val.score,
            odd_even_flag=stat_val.odd_even_flag,
            shape_flag=stat_val.shape_flag,
            depth_stability_flag=stat_val.depth_stability_flag,
            snr=candidate.snr or 0.0,
            depth=candidate.depth or 0.001,
            period=candidate.period or 1.0,
            duration=candidate.duration or 0.1,
        )

        # ── Persist ──────────────────────────────────────────────────────────
        validation = ValidationResult(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            ml_confidence=ml_confidence,
            ml_label=ml_label,
            statistical_score=stat_val.score,
            composite_score=fp_class.composite_score,
            fp_category=fp_class.category,
            odd_even_flag=stat_val.odd_even_flag,
            shape_flag=stat_val.shape_flag,
            depth_stability_flag=stat_val.depth_stability_flag,
            details={**stat_val.details, **fp_class.reasoning},
            shap_values=shap_values,
        )
        db.add(validation)
        await db.commit()
        await db.refresh(validation)
        return ValidationOut.model_validate(validation)

    except Exception as exc:
        logger.error("Validation failed for candidate %s: %s", candidate_id, exc)
        raise HTTPException(500, f"Validation failed: {exc}")


@router.get("/{candidate_id}", response_model=ValidationOut, summary="Get validation result for a candidate")
async def get_validation(candidate_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ValidationResult).where(ValidationResult.candidate_id == candidate_id)
    )
    val = result.scalar_one_or_none()
    if not val:
        raise HTTPException(404, "Validation result not found. Run validation first.")
    return ValidationOut.model_validate(val)
