"""
backend/models/orm.py
SQLAlchemy ORM models for all platform entities.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ─── Dataset ──────────────────────────────────────────────────────────────────
class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tic_id: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[str] = mapped_column(String(50), default="upload")  # upload | mast
    sector: Mapped[Optional[int]] = mapped_column(Integer)
    file_path: Mapped[Optional[str]] = mapped_column(String(512))
    file_type: Mapped[Optional[str]] = mapped_column(String(20))  # fits | csv
    num_points: Mapped[Optional[int]] = mapped_column(Integer)
    time_start: Mapped[Optional[float]] = mapped_column(Float)
    time_end: Mapped[Optional[float]] = mapped_column(Float)
    stellar_radius: Mapped[Optional[float]] = mapped_column(Float)
    stellar_mass: Mapped[Optional[float]] = mapped_column(Float)
    stellar_teff: Mapped[Optional[float]] = mapped_column(Float)
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    jobs: Mapped[list["ProcessingJob"]] = relationship("ProcessingJob", back_populates="dataset", cascade="all, delete-orphan")
    candidates: Mapped[list["TransitCandidate"]] = relationship("TransitCandidate", back_populates="dataset", cascade="all, delete-orphan")


# ─── Processing Job ───────────────────────────────────────────────────────────
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False)
    job_type: Mapped[str] = mapped_column(String(50))  # preprocessing | detection | validation | characterization
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | running | completed | failed
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[Optional[str]] = mapped_column(Text)
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="jobs")


# ─── Transit Candidate ────────────────────────────────────────────────────────
class TransitCandidate(Base):
    __tablename__ = "transit_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id"), nullable=False)
    method: Mapped[str] = mapped_column(String(20))  # TLS | BLS
    period: Mapped[Optional[float]] = mapped_column(Float)
    epoch: Mapped[Optional[float]] = mapped_column(Float)
    duration: Mapped[Optional[float]] = mapped_column(Float)
    depth: Mapped[Optional[float]] = mapped_column(Float)
    snr: Mapped[Optional[float]] = mapped_column(Float)
    sde: Mapped[Optional[float]] = mapped_column(Float)   # Signal Detection Efficiency (TLS)
    num_transits: Mapped[Optional[int]] = mapped_column(Integer)
    odd_even_mismatch: Mapped[Optional[float]] = mapped_column(Float)
    transit_data: Mapped[Optional[dict]] = mapped_column(JSON)  # folded curve, model fit
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="candidates")
    validation: Mapped[Optional["ValidationResult"]] = relationship("ValidationResult", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    characterization: Mapped[Optional["PlanetCharacterization"]] = relationship("PlanetCharacterization", back_populates="candidate", uselist=False, cascade="all, delete-orphan")


# ─── Validation Result ────────────────────────────────────────────────────────
class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("transit_candidates.id"), nullable=False)
    ml_confidence: Mapped[Optional[float]] = mapped_column(Float)
    ml_label: Mapped[Optional[str]] = mapped_column(String(30))  # PLANET | FALSE_POSITIVE | UNKNOWN
    statistical_score: Mapped[Optional[float]] = mapped_column(Float)
    composite_score: Mapped[Optional[float]] = mapped_column(Float)
    fp_category: Mapped[Optional[str]] = mapped_column(String(50))  # eclipsing_binary | background_eb | instrumental | planet_candidate
    odd_even_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    shape_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    depth_stability_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    shap_values: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    candidate: Mapped["TransitCandidate"] = relationship("TransitCandidate", back_populates="validation")


# ─── Planet Characterization ──────────────────────────────────────────────────
class PlanetCharacterization(Base):
    __tablename__ = "planet_characterizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("transit_candidates.id"), nullable=False)
    planet_radius_rearth: Mapped[Optional[float]] = mapped_column(Float)
    planet_radius_rjup: Mapped[Optional[float]] = mapped_column(Float)
    semi_major_axis_au: Mapped[Optional[float]] = mapped_column(Float)
    equilibrium_temp_k: Mapped[Optional[float]] = mapped_column(Float)
    orbital_inclination_deg: Mapped[Optional[float]] = mapped_column(Float)
    stellar_radius_rsun: Mapped[Optional[float]] = mapped_column(Float)
    stellar_mass_msun: Mapped[Optional[float]] = mapped_column(Float)
    stellar_teff_k: Mapped[Optional[float]] = mapped_column(Float)
    classification: Mapped[Optional[str]] = mapped_column(String(50))  # Super-Earth | Sub-Neptune | Hot Jupiter | etc.
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    candidate: Mapped["TransitCandidate"] = relationship("TransitCandidate", back_populates="characterization")
