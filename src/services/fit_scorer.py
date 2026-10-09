"""Semantic & Heuristic Fit Scoring Engine.

Evaluates match score and structured reasons between CandidateProfile and JobPosting.
"""

from __future__ import annotations

import re
from typing import Any

from src.models.job import JobPosting
from src.models.profile import CandidateProfile


class FitScorer:
    """Evaluates candidate-to-job fit score and structured match reasons."""

    def __init__(self, blacklisted_companies: list[str] | None = None):
        self.blacklisted_companies = [c.lower() for c in (blacklisted_companies or [])]

    def evaluate_fit(
        self,
        profile: CandidateProfile,
        job: JobPosting,
    ) -> tuple[float, bool, dict[str, Any]]:
        """Evaluate fit score, hard filter pass, and detailed match reasons.

        Returns:
            (fit_score, passes_hard_filters, match_reasons_dict)
        """
        company_name = (job.company or "").lower()

        # Hard Filter 1: Blacklisted company check
        if any(b in company_name for b in self.blacklisted_companies):
            return 0.0, False, {
                "hard_filter_pass": False,
                "rejection_reason": "Blacklisted company",
                "matched_skills": [],
                "missing_skills": [],
                "overall_score": 0.0,
            }

        # Collect candidate skills & keywords
        candidate_skills = [s.lower() for s in (profile.skills or [])]
        candidate_keywords = [k.lower() for k in (profile.keywords or [])]
        all_candidate_terms = set(candidate_skills + candidate_keywords)

        # Analyze job title and description
        job_text = f"{job.title or ''} {job.description or ''}".lower()
        title_lower = (job.title or "").lower()

        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for skill in (profile.skills or []):
            skill_lower = skill.lower()
            if re.search(r"\b" + re.escape(skill_lower) + r"\b", job_text):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Calculate keyword overlap score
        skill_score = (
            len(matched_skills) / len(profile.skills)
            if profile.skills
            else 0.5
        )

        # Title keyword match bonus
        title_match_bonus = 0.0
        if any(term in title_lower for term in all_candidate_terms if len(term) > 2):
            title_match_bonus = 0.2

        # Overall fit score calculation (0.0 to 1.0)
        overall_score = min(1.0, (skill_score * 0.8) + title_match_bonus)
        overall_score = round(overall_score, 2)

        match_reasons = {
            "hard_filter_pass": True,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_match_rate": round(skill_score, 2),
            "title_bonus": title_match_bonus > 0,
            "overall_score": overall_score,
        }

        return overall_score, True, match_reasons
