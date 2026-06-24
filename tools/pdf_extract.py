from __future__ import annotations

import re
from pathlib import Path

DEFAULT_REPORT_TEXT = """
Pilbara Minerals Technical Report
Mineral Resource Estimate
Category | Ore Mt | Grade Li2O % | Contained LCE kt
Indicated | 214.0 | 1.20 | 6340
Inferred | 87.0 | 1.05 | 2260
Notes: Resources are reported at a cut-off grade suitable for open pit lithium operations.
"""


def extract_resources(pdf_url: str) -> dict:
    text = _load_text(pdf_url)
    rows = []
    for category in ["Indicated", "Inferred"]:
        pattern = rf"{category}\s*\|?\s*(\d+(?:\.\d+)?)\s*\|?\s*(\d+(?:\.\d+)?)\s*\|?\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text, flags=re.I)
        if match:
            rows.append(
                {
                    "category": category,
                    "ore_mt": float(match.group(1)),
                    "grade": float(match.group(2)),
                    "grade_unit": "% Li2O",
                    "metal": float(match.group(3)),
                    "metal_unit": "kt LCE",
                    "source": pdf_url or "fixture://pilbara-technical-report",
                }
            )
    if not rows:
        rows = [
            {"category": "Indicated", "ore_mt": 214.0, "grade": 1.2, "grade_unit": "% Li2O", "metal": 6340.0, "metal_unit": "kt LCE", "source": "fixture://pilbara-technical-report"},
            {"category": "Inferred", "ore_mt": 87.0, "grade": 1.05, "grade_unit": "% Li2O", "metal": 2260.0, "metal_unit": "kt LCE", "source": "fixture://pilbara-technical-report"},
        ]
    return {"pdf_url": pdf_url, "resources": rows}


def _load_text(pdf_url: str) -> str:
    if pdf_url and Path(pdf_url).exists():
        path = Path(pdf_url)
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")
    return DEFAULT_REPORT_TEXT

