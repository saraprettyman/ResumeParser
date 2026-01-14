# pylint: disable=duplicate-code
"""Tests for SkillsChecker to ensure general skills are correctly extracted."""

from typing import Any
from resume_parser.utils.skills_checker import SkillsChecker


def test_general_skills_extraction(fake_resume_path: Any):
    """
    Validates that SkillsChecker correctly extracts key general skills
    from a fake resume file.
    """
    checker = SkillsChecker()
    skills = checker.extract_general_skills(str(fake_resume_path))

    # Flatten the found skills across all categories
    found_skills = {
        skill
        for category in skills.values()
        for skill in category["found"]
    }

    assert "Python" in found_skills, "'Python' should be detected in found skills"
    assert "AWS" in found_skills, "'AWS' should be detected in found skills"
    assert any(
        s.lower() == "machine learning" for s in found_skills
    ), "'machine learning' should be detected in found skills"


def test_job_description_comparison(fake_resume_path: Any, fake_job_description_path: Any):
    """
    Ensures resume vs job description comparison highlights matches and gaps.
    """
    checker = SkillsChecker()
    comparison = checker.compare_with_job_description(
        str(fake_resume_path),
        str(fake_job_description_path),
    )

    assert comparison, "Comparison should return categories with overlapping data"

    cloud_category = comparison.get("Cloud & DevOps", {})
    assert "AWS" in cloud_category.get("matching", []), "AWS should be marked as a matched skill"
    assert "AWS" in set(cloud_category.get("resume_exact", [])), "AWS: verbatim resume match issue"

    assert any(
        data.get("job_only")
        for data in comparison.values()
    ), "At least one skill should exist only in the job description"
