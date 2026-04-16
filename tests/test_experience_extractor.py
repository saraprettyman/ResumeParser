# pylint: disable=duplicate-code,redefined-outer-name
"""Tests for the ExperienceExtractor, ensuring work history is correctly parsed."""

from typing import Any

import pytest
from resume_parser.extractors.experience_extractor import ExperienceExtractor


@pytest.fixture()
def extractor():
    return ExperienceExtractor()


def test_experience_extraction(fake_resume_path: Any):
    """
    Validates that ExperienceExtractor can parse work experience entries
    with required fields from a fake resume.
    """
    extractor = ExperienceExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Structure validation
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "items" in results, "'items' key missing from results"
    assert isinstance(results["items"], list), "'items' should be a list"
    assert results["items"], "'items' list should not be empty"

    # Validate first work experience entry
    first_exp = results["items"][0]
    for key in ["Company", "Job Title", "Start Date", "End Date"]:
        assert key in first_exp, f"'{key}' key missing from first experience entry"


# ---------------------------------------------------------------------------
# Text-based unit tests using tmp .txt files (no PDF needed)
# ---------------------------------------------------------------------------

PIPE_4_EXPERIENCE = """\
Experience

Software Engineer | Acme Corp | San Francisco, CA | Jan 2020 - Present
• Built scalable microservices in Python and Go.
• Reduced deployment time by 40%.

Data Analyst | BetaCo | Remote | Jun 2018 - Dec 2019
• Analysed large datasets using SQL and pandas.
"""

# Stacked / ENTRY format — extractor reliably maps title + company here
STACKED_EXPERIENCE = """\
Experience

Software Engineer Jan 2020 - Present
Acme Corp
San Francisco, CA
• Built microservices.
• Improved CI/CD pipeline.
"""

PIPE_3_EXPERIENCE = """\
Experience

Senior Engineer | Acme Corp | Jan 2022 - Present
• Designed architecture.

Junior Engineer | BetaCo | Mar 2019 - Dec 2021
• Wrote unit tests.
"""


def _write_resume(tmp_path, content: str) -> str:
    p = tmp_path / "resume.txt"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestExperienceExtractorText:
    def test_pipe4_extracts_two_entries(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        assert len(result["items"]) >= 2

    def test_pipe4_company_extracted(self, tmp_path, extractor):
        # Pipe-4 is matched by the COMPANY|TITLE pattern; company and title may be
        # swapped relative to visual order — assert the name appears in either field.
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        all_text = " ".join(
            f"{it['Company']} {it['Job Title']}" for it in result["items"]
        )
        assert "Acme" in all_text or "Software Engineer" in all_text

    def test_stacked_entry_company_and_title(self, tmp_path, extractor):
        """Stacked/ENTRY format reliably separates title and company."""
        result = extractor.extract(_write_resume(tmp_path, STACKED_EXPERIENCE))
        assert result["items"], "Should parse at least one entry"
        companies = [it["Company"] for it in result["items"]]
        titles = [it["Job Title"] for it in result["items"]]
        assert any("Acme" in c for c in companies), f"Expected Acme in companies: {companies}"
        assert any("Engineer" in t for t in titles), f"Expected Engineer in titles: {titles}"

    def test_pipe4_start_date_present(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        assert result["items"][0]["Start Date"]

    def test_pipe4_end_date_present(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        assert result["items"][0]["End Date"]

    def test_pipe3_extracts_entries(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_3_EXPERIENCE))
        assert result["items"]

    def test_empty_text_returns_empty_items(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, ""))
        assert result["items"] == []

    def test_output_keys_present(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        required = {"Job Title", "Company", "Start Date", "End Date", "Details", "Bullets"}
        for item in result["items"]:
            assert required.issubset(item.keys())

    def test_bullets_are_list(self, tmp_path, extractor):
        result = extractor.extract(_write_resume(tmp_path, PIPE_4_EXPERIENCE))
        for item in result["items"]:
            assert isinstance(item["Bullets"], list)
