"""
backend/api/routes/characterization.py
Planet characterization endpoint.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from backend.models.orm import Dataset, TransitCandidate, PlanetCharacterization
from backend.models.schemas import CharacterizationOut
from backend.characterization.planet_params import estimate_planet_params
from backend.characterization.stellar_params import fetch_stellar_params

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/characterization", tags=["Planet Characterization"])


@router.post("/{candidate_id}", response_model=CharacterizationOut, summary="Estimate planet parameters")
async def characterize_planet(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Estimate planetary parameters for a validated transit candidate."""
    cand_result = await db.execute(select(TransitCandidate).where(TransitCandidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(404, "Candidate not found.")

    ds_result = await db.execute(select(Dataset).where(Dataset.id == candidate.dataset_id))
    dataset = ds_result.scalar_one_or_none()

    try:
        # Fetch stellar parameters from TIC if available
        if dataset and dataset.tic_id:
            stellar = fetch_stellar_params(dataset.tic_id)
        else:
            from backend.characterization.stellar_params import SOLAR_DEFAULTS
            stellar = SOLAR_DEFAULTS

        # Use DB stellar overrides if stored on dataset
        if dataset:
            if dataset.stellar_radius:
                stellar.radius_rsun = dataset.stellar_radius
            if dataset.stellar_mass:
                stellar.mass_msun = dataset.stellar_mass
            if dataset.stellar_teff:
                stellar.teff_k = dataset.stellar_teff

        planet = estimate_planet_params(
            candidate_id=candidate_id,
            period_days=candidate.period or 1.0,
            depth=candidate.depth or 0.001,
            duration_days=candidate.duration or 0.1,
            stellar_radius_rsun=stellar.radius_rsun,
            stellar_mass_msun=stellar.mass_msun,
            stellar_teff_k=stellar.teff_k,
        )

        char = PlanetCharacterization(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            planet_radius_rearth=planet.planet_radius_rearth,
            planet_radius_rjup=planet.planet_radius_rjup,
            semi_major_axis_au=planet.semi_major_axis_au,
            equilibrium_temp_k=planet.equilibrium_temp_k,
            orbital_inclination_deg=planet.orbital_inclination_deg,
            stellar_radius_rsun=stellar.radius_rsun,
            stellar_mass_msun=stellar.mass_msun,
            stellar_teff_k=stellar.teff_k,
            classification=planet.classification,
            details=planet.details,
        )
        db.add(char)
        await db.commit()
        await db.refresh(char)
        return CharacterizationOut.model_validate(char)

    except Exception as exc:
        logger.error("Characterization failed for %s: %s", candidate_id, exc)
        raise HTTPException(500, f"Characterization failed: {exc}")


@router.get("/{candidate_id}", response_model=CharacterizationOut)
async def get_characterization(candidate_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PlanetCharacterization).where(PlanetCharacterization.candidate_id == candidate_id)
    )
    char = result.scalar_one_or_none()
    if not char:
        raise HTTPException(404, "Characterization not found. Run characterization first.")
    return CharacterizationOut.model_validate(char)
