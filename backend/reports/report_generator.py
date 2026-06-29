"""
backend/reports/report_generator.py
PDF (ReportLab) and CSV report generation for exoplanet candidates.
"""
from __future__ import annotations

import csv
import io
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def generate_csv_report(
    dataset_name: str,
    candidates: List[Dict[str, Any]],
    output_dir: str,
) -> str:
    """Generate a CSV report with all candidate parameters."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{dataset_name}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    fieldnames = [
        "candidate_id", "method", "period_days", "epoch_btjd",
        "duration_days", "depth_ppm", "snr", "sde", "num_transits",
        "ml_label", "ml_confidence", "statistical_score", "composite_score",
        "fp_category", "planet_radius_rearth", "planet_radius_rjup",
        "semi_major_axis_au", "equilibrium_temp_k", "classification",
        "odd_even_flag", "shape_flag", "depth_stability_flag",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for c in candidates:
            row = {
                "candidate_id": c.get("id", ""),
                "method": c.get("method", ""),
                "period_days": round(c.get("period") or 0, 6),
                "epoch_btjd": round(c.get("epoch") or 0, 6),
                "duration_days": round(c.get("duration") or 0, 6),
                "depth_ppm": round((c.get("depth") or 0) * 1e6, 2),
                "snr": round(c.get("snr") or 0, 2),
                "sde": round(c.get("sde") or 0, 2),
                "num_transits": c.get("num_transits", 0),
                "ml_label": c.get("ml_label", ""),
                "ml_confidence": round(c.get("ml_confidence") or 0, 4),
                "statistical_score": round(c.get("statistical_score") or 0, 4),
                "composite_score": round(c.get("composite_score") or 0, 4),
                "fp_category": c.get("fp_category", ""),
                "planet_radius_rearth": round(c.get("planet_radius_rearth") or 0, 4),
                "planet_radius_rjup": round(c.get("planet_radius_rjup") or 0, 4),
                "semi_major_axis_au": round(c.get("semi_major_axis_au") or 0, 6),
                "equilibrium_temp_k": round(c.get("equilibrium_temp_k") or 0, 1),
                "classification": c.get("classification", ""),
                "odd_even_flag": c.get("odd_even_flag", False),
                "shape_flag": c.get("shape_flag", False),
                "depth_stability_flag": c.get("depth_stability_flag", False),
            }
            writer.writerow(row)

    logger.info("CSV report written: %s", filepath)
    return filepath


def generate_pdf_report(
    dataset_name: str,
    tic_id: Optional[str],
    candidates: List[Dict[str, Any]],
    preprocessing_summary: Optional[Dict[str, Any]],
    output_dir: str,
) -> str:
    """Generate a PDF scientific report using ReportLab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{dataset_name}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("title", fontSize=20, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=colors.HexColor("#0A1628"))
        subtitle_style = ParagraphStyle("subtitle", fontSize=12, fontName="Helvetica", alignment=TA_CENTER, textColor=colors.HexColor("#4B5563"))
        heading_style = ParagraphStyle("heading", fontSize=14, fontName="Helvetica-Bold", textColor=colors.HexColor("#0A1628"), spaceAfter=6)
        body_style = ParagraphStyle("body", fontSize=10, fontName="Helvetica", textColor=colors.HexColor("#374151"))
        accent_color = colors.HexColor("#FF6B35")
        navy_color = colors.HexColor("#0A1628")

        story = []

        # ── Header ────────────────────────────────────────────────────────────
        story.append(Paragraph("🔭 HORIZON EXOPLANET PLATFORM", title_style))
        story.append(Paragraph("Automated Transit Detection & Characterization Report", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=accent_color, spaceAfter=12))
        story.append(Spacer(1, 0.3*cm))

        meta_data = [
            ["Dataset", dataset_name],
            ["TIC ID", tic_id or "N/A"],
            ["Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
            ["Total Candidates", str(len(candidates))],
        ]
        meta_table = Table(meta_data, colWidths=[4*cm, 12*cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), navy_color),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.5*cm))

        # ── Preprocessing Summary ─────────────────────────────────────────────
        if preprocessing_summary:
            story.append(Paragraph("1. Preprocessing Summary", heading_style))
            pre_data = [["Parameter", "Value"]] + [
                [str(k).replace("_", " ").title(), str(v)]
                for k, v in preprocessing_summary.items()
            ]
            pre_table = Table(pre_data, colWidths=[8*cm, 8*cm])
            pre_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(pre_table)
            story.append(Spacer(1, 0.5*cm))

        # ── Candidate Table ───────────────────────────────────────────────────
        story.append(Paragraph("2. Detected Transit Candidates", heading_style))

        if not candidates:
            story.append(Paragraph("No transit candidates detected.", body_style))
        else:
            headers = ["ID", "Method", "Period (d)", "Depth (ppm)", "SNR", "ML Label", "Score", "Classification"]
            rows = [headers]
            for i, c in enumerate(candidates):
                rows.append([
                    str(i + 1),
                    c.get("method", ""),
                    f"{c.get('period', 0):.4f}",
                    f"{(c.get('depth', 0) or 0)*1e6:.0f}",
                    f"{c.get('snr', 0):.1f}",
                    c.get("ml_label", "—"),
                    f"{c.get('composite_score', 0):.3f}",
                    c.get("classification", "—"),
                ])
            col_widths = [1*cm, 2*cm, 2.5*cm, 2.5*cm, 1.5*cm, 3*cm, 2*cm, 3.5*cm]
            tbl = Table(rows, colWidths=col_widths)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            story.append(tbl)

        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            "Generated by Horizon Exoplanet Platform | NASA TESS Data Analysis | "
            f"{datetime.utcnow().strftime('%Y')}",
            ParagraphStyle("footer", fontSize=8, textColor=colors.HexColor("#9CA3AF"), alignment=TA_CENTER),
        ))

        doc.build(story)
        logger.info("PDF report written: %s", filepath)
        return filepath

    except ImportError:
        logger.error("ReportLab not installed — cannot generate PDF.")
        raise RuntimeError("ReportLab is required for PDF generation. Install with: pip install reportlab")
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        raise
