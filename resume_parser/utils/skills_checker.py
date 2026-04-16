"""
skills_checker.py

This module defines the SkillsChecker class, responsible for extracting and
matching technical skills from resume text against a predefined dataset.

Functionality:
    - Loads a comprehensive skills dataset from JSON via `load_skills`.
    - Retrieves role definitions and their associated skill categories.
    - Extracts all technical skills present in a resume.
    - Extracts role-specific technical skills from a resume.
    - Matches skills (including aliases) in a case-insensitive manner.

Classes:
    SkillsChecker:
        Provides methods for:
            - extract_general_skills(file_path): Extracts all skills across categories.
            - extract_role_skills(file_path, role): Extracts skills for a specific role.
            - load_roles(): Returns a list of available roles.
"""

import re
from typing import Any, Dict, List, Tuple, Optional

from resume_parser.utils.skills_list_loader import load_skills, load_roles
from resume_parser.utils.file_reader import read_resume


class SkillsChecker:  # pylint: disable=too-few-public-methods
    """
    A utility class for extracting and matching skills from resume text
    against a predefined skills dataset.

    The skills dataset is loaded from JSON using `load_skills` and includes:
      - "ALL_TECHNICAL_SKILLS": category -> skill definitions
      - "ROLES": role -> list of categories
    """

    def __init__(self) -> None:
        """Initialize the SkillsChecker by loading the complete skills dataset."""
        self.skills_data = load_skills()

    @staticmethod
    def load_roles() -> List[str]:
        """
        Retrieve the list of available roles.

        Returns:
            list[str]: Role names.
        """
        return load_roles()

    def extract_general_skills(self, file_path: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract all technical skills (across all categories) from a resume.
        """
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted: Dict[str, Dict[str, List[str]]] = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            found, missing, _ = self._match_skills(skills, resume_lower)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path: str, role: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract technical skills relevant to a specific role from a resume.
        """
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_categories = self.skills_data.get("ROLES", {}).get(role, [])
        extracted: Dict[str, Dict[str, List[str]]] = {}

        for category in role_categories:
            skills = self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).get(category, [])
            found, missing, _ = self._match_skills(skills, resume_lower)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def compare_with_job_description(
        self,
        resume_path: str,
        job_description_path: str,
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Compare resume skills with those mentioned in a job description.

        Args:
            resume_path: Path to the candidate's resume file.
            job_description_path: Path to the job description file.

        Returns:
            Mapping of skill categories to overlapping and missing skills, plus
            a record of canonical resume matches for display formatting.
        """
        resume_text = read_resume(resume_path).lower()
        job_text = read_resume(job_description_path).lower()
        comparison: Dict[str, Dict[str, List[str]]] = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            resume_found, _, resume_canonical = self._match_skills(skills, resume_text)
            job_found, _, _ = self._match_skills(skills, job_text)

            resume_set = set(resume_found)
            job_set = set(job_found)
            if not resume_set and not job_set:
                continue

            comparison[category] = {
                "matching": sorted(resume_set & job_set),
                "resume_only": sorted(resume_set - job_set),
                "job_only": sorted(job_set - resume_set),
                "resume_exact": sorted(resume_canonical),
            }

        return comparison

    def score_alignment(
        self,
        resume_path: str,
        job_description_path: str,
    ) -> Dict[str, Any]:
        """
        Score how well a resume aligns with a job description.

        The score is expressed as a percentage of skills mentioned in the job
        description that are also present in the resume.  A per-category
        breakdown is included so the caller can highlight the weakest areas.

        Args:
            resume_path: Path to the candidate's resume file.
            job_description_path: Path to the job description file.

        Returns:
            dict with keys:
                - "score" (float): overall match percentage (0–100).
                - "matched" (int): number of skills matching between resume and JD.
                - "total_in_jd" (int): total skills found in the job description.
                - "categories" (dict): per-category breakdown with
                  "matched", "total_in_jd", and "score" fields.
        """
        comparison = self.compare_with_job_description(resume_path, job_description_path)

        total_jd = 0
        total_matched = 0
        categories: Dict[str, Dict[str, Any]] = {}

        for category, data in comparison.items():
            cat_jd = len(data.get("matching", [])) + len(data.get("job_only", []))
            cat_matched = len(data.get("matching", []))
            cat_score = round((cat_matched / cat_jd * 100) if cat_jd else 0.0, 1)
            categories[category] = {
                "matched": cat_matched,
                "total_in_jd": cat_jd,
                "score": cat_score,
            }
            total_jd += cat_jd
            total_matched += cat_matched

        overall = round((total_matched / total_jd * 100) if total_jd else 0.0, 1)
        return {
            "score": overall,
            "matched": total_matched,
            "total_in_jd": total_jd,
            "categories": categories,
        }

    def _match_skills(
        self,
        skills: List[Dict[str, Any]],
        resume_lower: str,
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Match a list of skills against lowercase resume text.
        """
        found: List[str] = []
        missing: List[str] = []
        canonical_hits: List[str] = []

        for skill in skills:
            skill_names = [skill["name"].lower()] + [
                alias.lower() for alias in skill.get("aliases", [])
            ]
            matched_name: Optional[str] = None

            for name in skill_names:
                if re.search(rf"\b{re.escape(name)}\b", resume_lower):
                    matched_name = name
                    break

            if matched_name is not None:
                found.append(skill["name"])
                if matched_name == skill["name"].lower():
                    canonical_hits.append(skill["name"])
            else:
                missing.append(skill["name"])

        return found, missing, canonical_hits
