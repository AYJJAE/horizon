"""
backend/visualization/plot_generator.py
Generates JSON-serializable plot data for the frontend (Plotly.js).
All data is returned as dicts — no matplotlib rendering server-side.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def build_light_curve_plot(
    time: List[float],
    flux: List[float],
    flux_err: Optional[List[float]] = None,
    title: str = "Light Curve",
    color: str = "#4B9CD3",
) -> Dict[str, Any]:
    """Raw or cleaned light curve for Plotly scatter plot."""
    trace: Dict[str, Any] = {
        "x": time,
        "y": flux,
        "mode": "markers",
        "marker": {"color": color, "size": 2, "opacity": 0.7},
        "type": "scatter",
        "name": title,
    }
    if flux_err:
        trace["error_y"] = {
            "type": "data",
            "array": flux_err,
            "visible": True,
            "thickness": 0.5,
            "width": 0,
        }
    return {
        "data": [trace],
        "layout": {
            "title": {"text": title, "font": {"size": 14}},
            "xaxis": {"title": "Time (BTJD)", "showgrid": False},
            "yaxis": {"title": "Normalized Flux", "showgrid": True},
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "margin": {"l": 60, "r": 20, "t": 40, "b": 50},
            "hovermode": "closest",
        },
    }


def build_overlay_plot(
    raw_time: List[float],
    raw_flux: List[float],
    clean_time: List[float],
    clean_flux: List[float],
    trend: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Overlay plot: raw vs cleaned light curve + trend."""
    traces = [
        {
            "x": raw_time,
            "y": raw_flux,
            "mode": "markers",
            "marker": {"color": "#94A3B8", "size": 2, "opacity": 0.5},
            "name": "Raw",
            "type": "scatter",
        },
        {
            "x": clean_time,
            "y": clean_flux,
            "mode": "markers",
            "marker": {"color": "#3B82F6", "size": 2, "opacity": 0.8},
            "name": "Cleaned",
            "type": "scatter",
        },
    ]
    if trend:
        traces.append({
            "x": raw_time[:len(trend)],
            "y": trend,
            "mode": "lines",
            "line": {"color": "#F59E0B", "width": 1.5, "dash": "dash"},
            "name": "Trend",
            "type": "scatter",
        })
    return {
        "data": traces,
        "layout": {
            "title": {"text": "Raw vs Cleaned Light Curve"},
            "xaxis": {"title": "Time (BTJD)", "showgrid": False},
            "yaxis": {"title": "Flux"},
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "legend": {"x": 0.01, "y": 0.99},
            "margin": {"l": 60, "r": 20, "t": 40, "b": 50},
        },
    }


def build_periodogram_plot(
    periods: List[float],
    power: List[float],
    best_period: Optional[float] = None,
    method: str = "BLS",
) -> Dict[str, Any]:
    """BLS or TLS periodogram with best-period marker."""
    traces: List[Dict[str, Any]] = [
        {
            "x": periods,
            "y": power,
            "mode": "lines",
            "line": {"color": "#8B5CF6", "width": 1.5},
            "name": f"{method} Power",
            "type": "scatter",
        }
    ]
    shapes = []
    annotations = []
    if best_period:
        shapes.append({
            "type": "line",
            "x0": best_period, "x1": best_period,
            "y0": 0, "y1": max(power) if power else 1,
            "line": {"color": "#EF4444", "width": 2, "dash": "dot"},
        })
        annotations.append({
            "x": best_period,
            "y": max(power) if power else 1,
            "text": f"P={best_period:.3f}d",
            "showarrow": True,
            "arrowhead": 2,
            "font": {"color": "#EF4444"},
        })
    return {
        "data": traces,
        "layout": {
            "title": {"text": f"{method} Periodogram"},
            "xaxis": {"title": "Period (days)", "showgrid": False, "type": "log"},
            "yaxis": {"title": "Power"},
            "shapes": shapes,
            "annotations": annotations,
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "margin": {"l": 60, "r": 20, "t": 40, "b": 50},
        },
    }


def build_folded_transit_plot(
    folded_phase: List[float],
    folded_flux: List[float],
    model_flux: Optional[List[float]] = None,
    period: Optional[float] = None,
    depth: Optional[float] = None,
) -> Dict[str, Any]:
    """Phase-folded transit plot with model overlay."""
    traces: List[Dict[str, Any]] = [
        {
            "x": folded_phase,
            "y": folded_flux,
            "mode": "markers",
            "marker": {"color": "#06B6D4", "size": 3, "opacity": 0.6},
            "name": "Folded Data",
            "type": "scatter",
        }
    ]
    if model_flux:
        model_phase = list(np.linspace(
            min(folded_phase), max(folded_phase), len(model_flux)
        )) if folded_phase else []
        traces.append({
            "x": model_phase,
            "y": model_flux,
            "mode": "lines",
            "line": {"color": "#F43F5E", "width": 2},
            "name": "Transit Model",
            "type": "scatter",
        })
    title = "Phase-Folded Transit"
    if period:
        title += f" (P={period:.4f} d)"
    if depth:
        title += f" | Depth={depth*1e6:.0f} ppm"
    return {
        "data": traces,
        "layout": {
            "title": {"text": title},
            "xaxis": {"title": "Phase", "showgrid": False, "range": [-0.5, 0.5]},
            "yaxis": {"title": "Normalized Flux"},
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "margin": {"l": 60, "r": 20, "t": 50, "b": 50},
        },
    }


def build_detection_timeline(
    time: List[float],
    flux: List[float],
    transit_times: List[float],
    duration: float,
) -> Dict[str, Any]:
    """Light curve with transit windows highlighted."""
    shapes = []
    for tc in transit_times:
        shapes.append({
            "type": "rect",
            "x0": tc - duration / 2,
            "x1": tc + duration / 2,
            "y0": min(flux) - 0.001 if flux else 0,
            "y1": max(flux) + 0.001 if flux else 1,
            "fillcolor": "rgba(239, 68, 68, 0.15)",
            "line": {"width": 0},
        })
    return {
        "data": [
            {
                "x": time,
                "y": flux,
                "mode": "markers",
                "marker": {"color": "#3B82F6", "size": 2},
                "name": "Flux",
                "type": "scatter",
            }
        ],
        "layout": {
            "title": {"text": "Detected Transit Windows"},
            "xaxis": {"title": "Time (BTJD)", "showgrid": False},
            "yaxis": {"title": "Normalized Flux"},
            "shapes": shapes,
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "margin": {"l": 60, "r": 20, "t": 40, "b": 50},
        },
    }


def build_depth_bar_chart(
    candidate_ids: List[str],
    depths_ppm: List[float],
    snrs: List[float],
) -> Dict[str, Any]:
    """Bar chart of transit depths for all candidates."""
    return {
        "data": [
            {
                "x": candidate_ids,
                "y": depths_ppm,
                "type": "bar",
                "marker": {
                    "color": snrs,
                    "colorscale": "Viridis",
                    "colorbar": {"title": "SNR"},
                    "showscale": True,
                },
                "name": "Transit Depth",
                "text": [f"{d:.0f} ppm" for d in depths_ppm],
                "textposition": "auto",
            }
        ],
        "layout": {
            "title": {"text": "Transit Depths Comparison"},
            "xaxis": {"title": "Candidate ID"},
            "yaxis": {"title": "Depth (ppm)"},
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "margin": {"l": 60, "r": 20, "t": 40, "b": 80},
        },
    }
