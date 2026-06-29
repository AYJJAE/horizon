"""
backend/api/routes/reports.py
Report generation endpoint (PDF + CSV).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.core.config import settings
from backend.models.orm import Dataset, PlanetCharacterization, TransitCandidate, ValidationResult
from backend.models.schemas import ReportOut, ReportRequest
from backend.reports.report_generator import generate_csv_report, generate_pdf_report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportOut, summary="Generate PDF and/or CSV reports")
async def generate_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    """Generate downloadable scientific reports for all candidates of a dataset."""
    ds_result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = ds_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    # Fetch all related data
    cand_result = await db.execute(
        select(TransitCandidate).where(TransitCandidate.dataset_id == request.dataset_id)
    )
    candidates = cand_result.scalars().all()

    # Build enriched candidate dicts
    enriched: List[Dict[str, Any]] = []
    for c in candidates:
        row: Dict[str, Any] = {
            "id": c.id, "method": c.method,
            "period": c.period, "epoch": c.epoch,
            "duration": c.duration, "depth": c.depth,
            "snr": c.snr, "sde": c.sde,
            "num_transits": c.num_transits,
        }
        # Validation
        val_result = await db.execute(
            select(ValidationResult).where(ValidationResult.candidate_id == c.id)
        )
        val = val_result.scalar_one_or_none()
        if val:
            row.update({
                "ml_label": val.ml_label, "ml_confidence": val.ml_confidence,
                "statistical_score": val.statistical_score,
                "composite_score": val.composite_score,
                "fp_category": val.fp_category,
                "odd_even_flag": val.odd_even_flag,
                "shape_flag": val.shape_flag,
                "depth_stability_flag": val.depth_stability_flag,
            })
        # Characterization
        char_result = await db.execute(
            select(PlanetCharacterization).where(PlanetCharacterization.candidate_id == c.id)
        )
        char = char_result.scalar_one_or_none()
        if char:
            row.update({
                "planet_radius_rearth": char.planet_radius_rearth,
                "planet_radius_rjup": char.planet_radius_rjup,
                "semi_major_axis_au": char.semi_major_axis_au,
                "equilibrium_temp_k": char.equilibrium_temp_k,
                "classification": char.classification,
            })
        enriched.append(row)

    output_dir = settings.reports_dir
    os.makedirs(output_dir, exist_ok=True)
    dataset_name = (dataset.name or dataset.id).replace(" ", "_")

    pdf_path = None
    csv_path = None

    if request.format in ("pdf", "both"):
        pdf_path = generate_pdf_report(
            dataset_name=dataset_name,
            tic_id=dataset.tic_id,
            candidates=enriched,
            preprocessing_summary=None,
            output_dir=output_dir,
        )

    if request.format in ("csv", "both"):
        csv_path = generate_csv_report(
            dataset_name=dataset_name,
            candidates=enriched,
            output_dir=output_dir,
        )

    return ReportOut(
        dataset_id=request.dataset_id,
        pdf_path=pdf_path,
        csv_path=csv_path,
        generated_at=datetime.utcnow(),
    )


@router.get("/download/{filename}", summary="Download a generated report file")
async def download_report(filename: str):
    """Stream a generated PDF or CSV file for download."""
    output_dir = settings.reports_dir
    filepath = os.path.join(output_dir, filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(404, "Report file not found.")
    media_type = "application/pdf" if filename.endswith(".pdf") else "text/csv"
    return FileResponse(filepath, media_type=media_type, filename=filename)
