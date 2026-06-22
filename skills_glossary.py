"""Load and search the Hinglish-friendly skills glossary."""

import json
import re
from functools import lru_cache
from pathlib import Path

GLOSSARY_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_glossary.json"


@lru_cache(maxsize=1)
def load_glossary() -> dict[str, list[str]]:
    """Load skill aliases from JSON (cached after first read)."""
    with GLOSSARY_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _normalize(text: str) -> str:
    """Lowercase text and collapse extra whitespace for matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills_from_text(text: str) -> list[str]:
    """
    Find canonical skills in free text using alias matching.

    Supports abbreviations (ML, AI, DS), mixed casing, and common Hinglish phrases.
    """
    normalized = _normalize(text)
    found: set[str] = set()
    glossary = load_glossary()

    for canonical, aliases in glossary.items():
        if canonical == "hinglish_tech_phrases":
            continue

        for alias in aliases:
            alias_norm = _normalize(alias)

            # Word boundaries prevent "java" matching inside "javascript"
            if " " in alias_norm:
                pattern = re.escape(alias_norm)
            else:
                pattern = rf"\b{re.escape(alias_norm)}\b"

            if re.search(pattern, normalized):
                found.add(canonical.title())
                break

    # Map Hinglish phrases to related canonical skills
    hinglish_map = {
        "machine learning wala": "Machine Learning",
        "ai ka kaam": "Artificial Intelligence",
        "data science field": "Data Science",
        "python seekha": "Python",
        "coding karta": "Problem Solving",
        "developer hun": "Problem Solving",
        "full stack": "Javascript",
        "backend developer": "Rest Api",
        "frontend developer": "Html",
        "computer science": "Problem Solving",
        "cse": "Problem Solving",
        "it branch": "Problem Solving",
    }

    for phrase, skill in hinglish_map.items():
        if phrase in normalized:
            found.add(skill)

    return sorted(found)


def extract_skills_from_job_description(job_text: str) -> list[str]:
    """Extract required skills from a job description using the same glossary."""
    return extract_skills_from_text(job_text)
