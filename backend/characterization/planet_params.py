"""
backend/characterization/planet_params.py
Estimate planetary parameters from transit geometry + stellar parameters.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Physical constants (SI)
G = 6.674e-11               # m^3 kg^-1 s^-2
M_SUN_KG = 1.989e30         # kg
R_SUN_M = 6.957e8           # m
R_EARTH_M = 6.371e6         # m
R_JUP_M = 7.1492e7          # m
AU_M = 1.496e11             # m
L_SUN_W = 3.828e26          # W
SIGMA_SB = 5.67e-8          # Stefan-Boltzmann constant

# Planet size classification boundaries (in Earth radii)
PLANET_CLASSES = [
    (1.25, "Rocky Earth-sized"),
    (2.0, "Super-Earth"),
    (4.0, "Sub-Neptune"),
    (6.0, "Neptune-sized"),
    (15.0, "Sub-Saturn"),
    (float("inf"), "Gas Giant / Hot Jupiter"),
]


@dataclass
class PlanetParams:
    candidate_id: str
    period_days: float
    depth: float

    # Derived parameters
    planet_radius_rearth: Optional[float] = None
    planet_radius_rjup: Optional[float] = None
    semi_major_axis_au: Optional[float] = None
    equilibrium_temp_k: Optional[float] = None
    orbital_inclination_deg: Optional[float] = None
    stellar_radius_rsun: Optional[float] = None
    stellar_mass_msun: Optional[float] = None
    stellar_teff_k: Optional[float] = None
    classification: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


def estimate_planet_params(
    candidate_id: str,
    period_days: float,
    depth: float,            # fractional transit depth
    duration_days: float,
    stellar_radius_rsun: float = 1.0,
    stellar_mass_msun: float = 1.0,
    stellar_teff_k: float = 5778.0,
    albedo: float = 0.3,     # Bond albedo for equilibrium temperature
) -> PlanetParams:
    """
    Estimate all planetary parameters from transit observables.

    Parameters
    ----------
    period_days       : orbital period
    depth             : fractional flux decrease during transit (e.g. 0.01 = 1%)
    duration_days     : total transit duration (first to last contact)
    stellar_*         : host star properties
    albedo            : assumed planetary Bond albedo (default 0.3)
    """
    params = PlanetParams(
        candidate_id=candidate_id,
        period_days=period_days,
        depth=depth,
        stellar_radius_rsun=stellar_radius_rsun,
        stellar_mass_msun=stellar_mass_msun,
        stellar_teff_k=stellar_teff_k,
    )

    details: Dict[str, Any] = {}

    # ── Planet Radius ─────────────────────────────────────────────────────────
    # R_p / R_* = sqrt(delta)
    rp_rs = math.sqrt(max(0, depth))
    r_star_m = stellar_radius_rsun * R_SUN_M
    rp_m = rp_rs * r_star_m
    params.planet_radius_rearth = rp_m / R_EARTH_M
    params.planet_radius_rjup = rp_m / R_JUP_M
    details["rp_rs_ratio"] = round(rp_rs, 6)
    details["planet_radius_km"] = round(rp_m / 1000, 1)

    # ── Semi-Major Axis ───────────────────────────────────────────────────────
    # Kepler's 3rd Law: a^3 / P^2 = G*M_* / (4*pi^2)
    T_s = period_days * 86400.0          # period in seconds
    M_star_kg = stellar_mass_msun * M_SUN_KG
    a_m = (G * M_star_kg * T_s**2 / (4 * math.pi**2)) ** (1 / 3)
    params.semi_major_axis_au = a_m / AU_M
    details["semi_major_axis_m"] = round(a_m, 2)

    # ── Equilibrium Temperature ───────────────────────────────────────────────
    # T_eq = T_* * sqrt(R_* / 2a) * (1 - albedo)^(1/4)
    if a_m > 0:
        teq = stellar_teff_k * math.sqrt(r_star_m / (2 * a_m)) * (1 - albedo) ** 0.25
        params.equilibrium_temp_k = teq
        details["habitable_zone"] = _habitable_zone_check(teq)

    # ── Orbital Inclination ───────────────────────────────────────────────────
    # b = a/R_* * cos(i)  →  from transit duration:
    # cos(i) ≈ sqrt(1 - (duration * pi / period)^2 * (a/R_*)^2) — simplified
    try:
        a_rs = a_m / r_star_m
        tau_ratio = (math.pi * duration_days / period_days)
        cos_i_sq = (rp_rs ** 2 - (tau_ratio * a_rs) ** 2) / (1 - (tau_ratio * a_rs) ** 2)
        if 0 <= cos_i_sq <= 1:
            inclination = math.degrees(math.acos(math.sqrt(max(0, cos_i_sq))))
            params.orbital_inclination_deg = inclination
    except (ValueError, ZeroDivisionError):
        pass

    # ── Planet Classification ─────────────────────────────────────────────────
    if params.planet_radius_rearth is not None:
        for max_r, cls_name in PLANET_CLASSES:
            if params.planet_radius_rearth < max_r:
                params.classification = cls_name
                break

    details["depth_ppm"] = round(depth * 1e6, 1)
    details["transit_duration_hours"] = round(duration_days * 24, 3)
    params.details = details

    logger.info(
        "Characterization [%s]: Rp=%.2f Re, a=%.4f AU, Teq=%.0f K, class=%s",
        candidate_id,
        params.planet_radius_rearth or 0,
        params.semi_major_axis_au or 0,
        params.equilibrium_temp_k or 0,
        params.classification,
    )
    return params


def _habitable_zone_check(teq_k: float) -> str:
    """Rough habitable zone classification based on equilibrium temperature."""
    if teq_k < 150:
        return "frozen"
    elif teq_k < 250:
        return "cold_edge"
    elif teq_k < 320:
        return "habitable_zone"
    elif teq_k < 500:
        return "warm_edge"
    else:
        return "hot_zone"
