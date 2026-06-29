"""
backend/models/schemas.py
Pydantic v2 request/response schemas for all API endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ─── Shared ───────────────────────────────────────────────────────────────────
class OKResponse(BaseModel):
    ok: bool = True
    message: str = "Success"


# ─── Dataset ──────────────────────────────────────────────────────────────────
class DatasetBase(BaseModel):
    name: str
    tic_id: Optional[str] = None
    source: str = "upload"
    sector: Optional[int] = None


class DatasetCreate(DatasetBase):
    pass


class DatasetOut(DatasetBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    file_type: Optional[str] = None
    num_points: Optional[int] = None
    time_start: Optional[float] = None
    time_end: Optional[float] = None
    stellar_radius: Optional[float] = None
    stellar_mass: Optional[float] = None
    stellar_teff: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime


class DatasetPreview(BaseModel):
    id: str
    name: str
    time: List[float]
    flux: List[float]
    flux_err: Optional[List[float]] = None
    num_points: int
    time_unit: str = "BTJD"


class TESSSearchResult(BaseModel):
    tic_id: str
    sector: int
    exptime: Optional[float] = None
    mission: str
    description: str


# ─── Processing Job ───────────────────────────────────────────────────────────
class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    dataset_id: str
    job_type: str
    status: str
    progress: int
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


# ─── Preprocessing ────────────────────────────────────────────────────────────
class PreprocessingConfig(BaseModel):
    sigma_clip: float = Field(default=4.0, ge=1.0, le=10.0)
    detrend_method: str = Field(default="savgol", pattern="^(savgol|spline|wotan)$")
    savgol_window: int = Field(default=51, ge=5)
    interpolate: bool = True
    normalize: bool = True


class PreprocessingResult(BaseModel):
    dataset_id: str
    job_id: str
    raw_time: List[float]
    raw_flux: List[float]
    clean_time: List[float]
    clean_flux: List[float]
    detrended_flux: List[float]
    trend: List[float]
    outliers_removed: int
    gaps_interpolated: int
    summary: Dict[str, Any]


# ─── Transit Detection ────────────────────────────────────────────────────────
class DetectionConfig(BaseModel):
    method: str = Field(default="both", pattern="^(tls|bls|both)$")
    min_period: float = Field(default=0.5, gt=0)
    max_period: float = Field(default=27.0, gt=0)
    snr_threshold: float = Field(default=7.0, gt=0)


class TransitCandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    dataset_id: str
    method: str
    period: Optional[float] = None
    epoch: Optional[float] = None
    duration: Optional[float] = None
    depth: Optional[float] = None
    snr: Optional[float] = None
    sde: Optional[float] = None
    num_transits: Optional[int] = None
    odd_even_mismatch: Optional[float] = None
    created_at: datetime


class DetectionResult(BaseModel):
    dataset_id: str
    job_id: str
    num_candidates: int
    candidates: List[TransitCandidateOut]
    periodogram: Optional[Dict[str, Any]] = None


# ─── Validation ───────────────────────────────────────────────────────────────
class ValidationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_id: str
    ml_confidence: Optional[float] = None
    ml_label: Optional[str] = None
    statistical_score: Optional[float] = None
    composite_score: Optional[float] = None
    fp_category: Optional[str] = None
    odd_even_flag: bool
    shape_flag: bool
    depth_stability_flag: bool
    details: Optional[Dict[str, Any]] = None
    shap_values: Optional[Dict[str, Any]] = None
    created_at: datetime


# ─── Characterization ─────────────────────────────────────────────────────────
class CharacterizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_id: str
    planet_radius_rearth: Optional[float] = None
    planet_radius_rjup: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    equilibrium_temp_k: Optional[float] = None
    orbital_inclination_deg: Optional[float] = None
    stellar_radius_rsun: Optional[float] = None
    stellar_mass_msun: Optional[float] = None
    stellar_teff_k: Optional[float] = None
    classification: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime


# ─── Visualization ───────────────────────────────────────────────────────────
class PlotDataResponse(BaseModel):
    dataset_id: str
    raw_light_curve: Optional[Dict[str, Any]] = None
    clean_light_curve: Optional[Dict[str, Any]] = None
    periodogram: Optional[Dict[str, Any]] = None
    folded_transit: Optional[Dict[str, Any]] = None
    transit_depth_chart: Optional[Dict[str, Any]] = None
    detection_timeline: Optional[Dict[str, Any]] = None


# ─── Reports ──────────────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    dataset_id: str
    format: str = Field(default="pdf", pattern="^(pdf|csv|both)$")
    include_plots: bool = True


class ReportOut(BaseModel):
    dataset_id: str
    pdf_path: Optional[str] = None
    csv_path: Optional[str] = None
    generated_at: datetime
