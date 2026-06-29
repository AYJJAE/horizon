"""
backend/characterization/stellar_params.py
Fetch stellar parameters from MAST TIC catalog via Astroquery.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Solar constants
R_SUN_KM = 695700.0        # km
R_EARTH_KM = 6371.0        # km
R_JUP_KM = 71492.0         # km


@dataclass
class StellarParams:
    tic_id: str
    radius_rsun: float      # Stellar radius in solar radii
    mass_msun: float        # Stellar mass in solar masses
    teff_k: float           # Effective temperature in Kelvin
    luminosity_lsun: Optional[float] = None
    logg: Optional[float] = None
    metallicity: Optional[float] = None
    source: str = "TIC"     # TIC | assumed_solar | user


SOLAR_DEFAULTS = StellarParams(
    tic_id="solar",
    radius_rsun=1.0,
    mass_msun=1.0,
    teff_k=5778.0,
    luminosity_lsun=1.0,
    logg=4.44,
    metallicity=0.0,
    source="assumed_solar",
)


def fetch_stellar_params(tic_id: str) -> StellarParams:
    """
    Query the MAST TIC catalog for stellar parameters.
    Falls back to solar defaults if the query fails or data is missing.
    """
    try:
        from astroquery.mast import Catalogs
        catalog_data = Catalogs.query_criteria(catalog="TIC", ID=int(tic_id))
        if len(catalog_data) == 0:
            logger.warning("TIC %s not found in catalog, using solar defaults.", tic_id)
            return _solar_with_tic(tic_id)

        row = catalog_data[0]

        def _safe_float(val, default: float) -> float:
            try:
                v = float(val)
                return v if not (v != v) else default  # NaN check
            except (TypeError, ValueError):
                return default

        params = StellarParams(
            tic_id=tic_id,
            radius_rsun=_safe_float(row.get("rad"), 1.0),
            mass_msun=_safe_float(row.get("mass"), 1.0),
            teff_k=_safe_float(row.get("Teff"), 5778.0),
            luminosity_lsun=_safe_float(row.get("lum"), None),
            logg=_safe_float(row.get("logg"), None),
            metallicity=_safe_float(row.get("MH"), None),
            source="TIC",
        )
        logger.info(
            "TIC %s: R=%.2f Rsun, M=%.2f Msun, Teff=%.0f K",
            tic_id, params.radius_rsun, params.mass_msun, params.teff_k,
        )
        return params

    except ImportError:
        logger.warning("Astroquery not installed, using solar defaults.")
        return _solar_with_tic(tic_id)
    except Exception as exc:
        logger.warning("TIC query failed for %s: %s. Using solar defaults.", tic_id, exc)
        return _solar_with_tic(tic_id)


def _solar_with_tic(tic_id: str) -> StellarParams:
    p = StellarParams(
        tic_id=tic_id,
        radius_rsun=SOLAR_DEFAULTS.radius_rsun,
        mass_msun=SOLAR_DEFAULTS.mass_msun,
        teff_k=SOLAR_DEFAULTS.teff_k,
        luminosity_lsun=SOLAR_DEFAULTS.luminosity_lsun,
        logg=SOLAR_DEFAULTS.logg,
        metallicity=SOLAR_DEFAULTS.metallicity,
        source="assumed_solar",
    )
    return p
