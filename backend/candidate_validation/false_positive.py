"""
backend/candidate_validation/false_positive.py
Composite false-positive classification combining ML and statistical scores.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# FP categories
FP_ECLIPSING_BINARY = "eclipsing_binary"
FP_BACKGROUND_EB = "background_eb"
FP_INSTRUMENTAL = "instrumental_artifact"
FP_PLANET_CANDIDATE = "planet_candidate"
FP_UNKNOWN = "unknown"


@dataclass
class FPClassification:
    category: str            # One of the FP_ constants above
    composite_score: float   # 0–1 (1 = confident planet)
    ml_confidence: float
    statistical_score: float
    reasoning: Dict[str, Any]


def classify_false_positive(
    ml_confidence: float,
    ml_label: str,
    statistical_score: float,
    odd_even_flag: bool,
    shape_flag: bool,
    depth_stability_flag: bool,
    snr: float,
    depth: float,
    period: float,
    duration: float,
) -> FPClassification:
    """
    Integrate ML and statistical validation results into a final
    false-positive classification and composite confidence score.

    Score interpretation:
      0.8–1.0 : Strong planet candidate
      0.5–0.8 : Possible planet candidate (needs follow-up)
      0.2–0.5 : Likely false positive
      0.0–0.2 : Strong false positive
    """
    # ── Composite Score ──────────────────────────────────────────────────────
    # Weight: ML 60%, Statistical 40%
    ml_weight = 0.60
    stat_weight = 0.40
    ml_score_raw = ml_confidence if ml_label == "PLANET" else (1.0 - ml_confidence)
    composite = ml_weight * ml_score_raw + stat_weight * statistical_score

    # ── FP Category Rules ────────────────────────────────────────────────────
    category = _determine_category(
        composite, odd_even_flag, shape_flag, depth_stability_flag,
        snr, depth, period, duration,
    )

    reasoning = {
        "ml_confidence": ml_confidence,
        "ml_label": ml_label,
        "statistical_score": statistical_score,
        "odd_even_flag": odd_even_flag,
        "shape_flag": shape_flag,
        "depth_stability_flag": depth_stability_flag,
        "composite_score": round(composite, 4),
        "category": category,
    }

    logger.info(
        "FP classification: category=%s, composite=%.3f (ML=%.3f, stat=%.3f)",
        category, composite, ml_score_raw, statistical_score,
    )

    return FPClassification(
        category=category,
        composite_score=round(composite, 4),
        ml_confidence=ml_confidence,
        statistical_score=statistical_score,
        reasoning=reasoning,
    )


def _determine_category(
    composite: float,
    odd_even_flag: bool,
    shape_flag: bool,
    depth_stability_flag: bool,
    snr: float,
    depth: float,
    period: float,
    duration: float,
) -> str:
    """Rule-based FP category determination."""
    # Strong odd-even mismatch → Eclipsing Binary (depth doubles at secondary eclipse)
    if odd_even_flag and depth > 0.01:
        return FP_ECLIPSING_BINARY

    # Non-trapezoidal shape + unstable depth → Background EB (blended)
    if shape_flag and depth_stability_flag:
        return FP_BACKGROUND_EB

    # Low SNR + no other flags → Instrumental artifact
    if snr < 5.0 and not odd_even_flag:
        return FP_INSTRUMENTAL

    # Composite score above 0.5 → Planet candidate
    if composite >= 0.5:
        return FP_PLANET_CANDIDATE

    return FP_UNKNOWN
