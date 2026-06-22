"""Helper utilities for JSON export and UI formatting."""

import json
from datetime import datetime, timezone
from typing import Any


def build_export_payload(
    parsed_resume: dict[str, Any],
    match_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine parsed resume and optional match analysis for download."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "resume": parsed_resume,
    }
    if match_result:
        payload["job_match"] = match_result
    return payload


def to_pretty_json(data: dict[str, Any]) -> str:
    """Return indented JSON string suitable for download."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def match_score_css(color_hex: str) -> str:
    """Inline CSS for the color-coded score badge in Streamlit."""
    return f"""
        background-color: {color_hex}22;
        border: 2px solid {color_hex};
        color: {color_hex};
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin: 0.5rem 0 1rem 0;
    """
