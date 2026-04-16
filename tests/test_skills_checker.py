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


def test_role_skills_extraction(fake_resume_path: Any):
    """
    Validates that extract_role_skills returns data only for the requested role's categories.
    """
    checker = SkillsChecker()
    roles = checker.load_roles()
    assert roles, "There should be at least one available role"

    role = roles[0]
    result = checker.extract_role_skills(str(fake_resume_path), role)
    assert isinstance(result, dict), "Role skills result should be a dict"
    for category, data in result.items():
        assert "found" in data, f"'found' key missing in category '{category}'"
        assert "missing" in data, f"'missing' key missing in category '{category}'"


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


def test_score_alignment_returns_expected_keys(
    fake_resume_path: Any, fake_job_description_path: Any
):
    """
    Validates the structure and range of score_alignment output.
    """
    checker = SkillsChecker()
    result = checker.score_alignment(str(fake_resume_path), str(fake_job_description_path))

    assert "score" in result, "'score' key missing"
    assert "matched" in result, "'matched' key missing"
    assert "total_in_jd" in result, "'total_in_jd' key missing"
    assert "categories" in result, "'categories' key missing"

    assert 0.0 <= result["score"] <= 100.0, "Score should be between 0 and 100"
    assert result["matched"] <= result["total_in_jd"], "Matched can't exceed total_in_jd"
    assert isinstance(result["categories"], dict)


def test_score_alignment_positive_match(fake_resume_path: Any, fake_job_description_path: Any):
    """
    Verifies that the fake resume scores above 0 against the bundled job description.
    """
    checker = SkillsChecker()
    result = checker.score_alignment(str(fake_resume_path), str(fake_job_description_path))
    assert result["matched"] > 0, "At least one skill should match between resume and JD"
    assert result["score"] > 0.0, "Alignment score should be positive"
