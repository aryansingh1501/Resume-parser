"""Compare resume skills against a job description and compute match score."""

from dataclasses import dataclass

from src.skills_glossary import extract_skills_from_job_description


@dataclass
class MatchResult:
    """Structured output from job-resume comparison."""

    match_score: float
    matched_skills: list[str]
    skill_gaps: list[str]
    job_skills: list[str]
    resume_skills: list[str]
    score_color: str
    score_label: str


def score_color_and_label(score: float) -> tuple[str, str]:
    """
    Map percentage to traffic-light colors for the dashboard.

    Red    = needs improvement (< 50%)
    Yellow = partial match (50–74%)
    Green  = strong match (75%+)
    """
    if score >= 75:
        return "#22c55e", "Strong Match"
    if score >= 50:
        return "#eab308", "Moderate Match"
    return "#ef4444", "Low Match"


def compare_with_job(resume_skills: list[str], job_description: str) -> MatchResult:
    """
    Compute match score using skill overlap.

    Formula:
        match_score = (matched_skills / job_skills) * 100

    If the job description yields no glossary skills, we fall back to a
    keyword overlap ratio so the user still gets feedback.
    """
    resume_set = {skill.lower() for skill in resume_skills}
    job_skills = extract_skills_from_job_description(job_description)
    job_set = {skill.lower() for skill in job_skills}

    matched = sorted(resume_set & job_set)
    gaps = sorted(job_set - resume_set)

    if job_set:
        score = round((len(matched) / len(job_set)) * 100, 1)
    else:
        # Fallback: compare unique words longer than 4 chars
        job_words = {
            word.lower()
            for word in job_description.split()
            if len(word) > 4 and word.isalpha()
        }
        resume_words = {
            word.lower()
            for word in " ".join(resume_skills).split()
            if len(word) > 3
        }
        overlap = job_words & resume_words
        score = round((len(overlap) / max(len(job_words), 1)) * 100, 1)
        matched = sorted(overlap)
        gaps = sorted(job_words - resume_words)[:15]

    color, label = score_color_and_label(score)

    return MatchResult(
        match_score=score,
        matched_skills=[skill.title() for skill in matched],
        skill_gaps=[skill.title() for skill in gaps],
        job_skills=[skill.title() for skill in sorted(job_set)] if job_set else [],
        resume_skills=resume_skills,
        score_color=color,
        score_label=label,
    )
