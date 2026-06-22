"""Extract structured fields from raw resume text using regex + spaCy NLP."""

import re
from typing import Any

import spacy

from src.skills_glossary import extract_skills_from_text

# Lazy-load spaCy so Streamlit startup stays fast
_NLP = None

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}\b"
)

EDUCATION_KEYWORDS = [
    "b.tech",
    "btech",
    "b.e",
    "b.e.",
    "bachelor",
    "b.sc",
    "bsc",
    "m.tech",
    "mtech",
    "master",
    "m.sc",
    "msc",
    "mba",
    "phd",
    "doctorate",
    "diploma",
    "intermediate",
    "12th",
    "10th",
    "high school",
    "computer science",
    "information technology",
    "engineering",
    "university",
    "college",
    "institute",
    "iit",
    "nit",
    "iiit",
]

EXPERIENCE_SECTION_HINTS = [
    "experience",
    "work history",
    "employment",
    "professional experience",
    "internship",
    "projects",
]

CERT_KEYWORDS = [
    "certified",
    "certification",
    "certificate",
    "aws certified",
    "azure certified",
    "google cloud certified",
    "pmp",
    "coursera",
    "udemy",
    "nptel",
    "oracle certified",
    "microsoft certified",
]


def get_nlp():
    """Load spaCy English model once and reuse it."""
    global _NLP
    if _NLP is None:
        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError as exc:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            ) from exc
    return _NLP


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def extract_name(text: str) -> str | None:
    """
    Try spaCy PERSON entity first, then fall back to the first non-empty line.

    Many student resumes put the name on line 1, so this heuristic works well.
    """
    nlp = get_nlp()
    doc = nlp(text[:1200])

    for ent in doc.ents:
        if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
            return ent.text.strip()

    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if EMAIL_PATTERN.search(cleaned) or PHONE_PATTERN.search(cleaned):
            continue
        if len(cleaned.split()) <= 5 and not any(char.isdigit() for char in cleaned):
            return cleaned

    return None


def extract_education(text: str) -> list[str]:
    """Pull education lines that contain degree or institution keywords."""
    education: list[str] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for index, line in enumerate(lines):
        lower = line.lower()
        if any(keyword in lower for keyword in EDUCATION_KEYWORDS):
            snippet = line
            # Include the next line if it looks like a year or institution detail
            if index + 1 < len(lines):
                next_line = lines[index + 1]
                if re.search(r"\b(20\d{2}|19\d{2}|present|cgpa|gpa|%)\b", next_line.lower()):
                    snippet = f"{line} | {next_line}"
            if snippet not in education:
                education.append(snippet)

    return education[:8]


def extract_experience(text: str) -> list[str]:
    """
    Capture experience-like lines using section hints and date patterns.

    Looks for year ranges (2022 - 2024) and role/company patterns.
    """
    experience: list[str] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    in_experience_section = False
    date_pattern = re.compile(
        r"\b(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|19\d{2}|present|current)\b",
        re.IGNORECASE,
    )

    for line in lines:
        lower = line.lower()

        if any(hint in lower for hint in EXPERIENCE_SECTION_HINTS):
            in_experience_section = True
            continue

        if in_experience_section and lower in {"education", "skills", "certifications", "projects"}:
            in_experience_section = False

        if date_pattern.search(line) or (
            in_experience_section and len(line) > 12 and not line.startswith("•")
        ):
            if line not in experience:
                experience.append(line)

    # Fallback: any line with a year range anywhere in the resume
    if not experience:
        for line in lines:
            if date_pattern.search(line) and line not in experience:
                experience.append(line)

    return experience[:10]


def extract_certifications(text: str) -> list[str]:
    """Find certification-related lines."""
    certifications: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        lower = cleaned.lower()
        if any(keyword in lower for keyword in CERT_KEYWORDS):
            certifications.append(cleaned)

    return certifications[:8]


def parse_resume(text: str) -> dict[str, Any]:
    """
    Main parser: turn raw resume text into a structured dictionary.

    Returns keys: name, email, phone, skills, education, experience, certifications, raw_text_preview
    """
    cleaned_text = re.sub(r"\r\n", "\n", text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    parsed = {
        "name": extract_name(cleaned_text),
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "skills": extract_skills_from_text(cleaned_text),
        "education": extract_education(cleaned_text),
        "experience": extract_experience(cleaned_text),
        "certifications": extract_certifications(cleaned_text),
        "raw_text_preview": cleaned_text[:1500],
    }

    return parsed
