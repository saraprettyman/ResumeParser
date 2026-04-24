# pylint: disable=duplicate-code,redefined-outer-name
"""Tests for the EducationExtractor, ensuring educational history is correctly parsed."""

from typing import Any

import pytest
from resume_parser.extractors.education_extractor import EducationExtractor


@pytest.fixture()
def extractor():
    return EducationExtractor()


def test_education_extraction(fake_resume_path: Any):
    """
    Validates that EducationExtractor can parse educational entries
    with required fields from a fake resume.
    """
    extractor = EducationExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Structure validation
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "items" in results, "'items' key missing from results"
    assert isinstance(results["items"], list), "'items' should be a list"
    assert results["items"], "'items' list should not be empty"

    # Validate first education entry
    edu_entry = results["items"][0]
    assert any(
        keyword in edu_entry["Degree & Emphasis"].lower()
        for keyword in ["bachelor", "master", "associate", "ph.d", "doctor"]
    ), "Degree & Emphasis should contain a valid degree keyword"
    assert edu_entry["Institution"], "Institution should not be empty"
    assert edu_entry["Graduation Date"], "Graduation Date should not be empty"


# ---------------------------------------------------------------------------
# Text-based unit tests for parse_education (no PDF needed)
# ---------------------------------------------------------------------------

EDUCATION_SECTION_BACHELOR = """\
State University
Logan, Utah
Bachelor of Science: Computer Science May 2021
GPA: 3.8/4.0
Minor: Mathematics
"""

EDUCATION_SECTION_MASTER = """\
MIT
Master's of Science in Data Science               December 2023
GPA: 4.0
"""

EDUCATION_SECTION_MULTI = """\
State University
Logan, Utah
Bachelor of Science: Computer Science  May 2021
GPA: 3.8/4.0
Minor: Mathematics

MIT
Master of Science in Data Science  December 2023
GPA: 4.0
"""

EDUCATION_SECTION_EMPTY = ""


class TestParseEducation:
    def test_empty_section_returns_empty_list(self, extractor):
        assert extractor.parse_education(EDUCATION_SECTION_EMPTY) == []

    def test_whitespace_only_returns_empty_list(self, extractor):
        assert extractor.parse_education("   \n\n  ") == []

    def test_bachelor_institution_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        assert items, "Should parse at least one entry"
        assert items[0]["Institution"], "Institution should not be empty"

    def test_bachelor_graduation_date_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        assert "2021" in items[0]["Graduation Date"]

    def test_bachelor_degree_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        degree = items[0]["Degree & Emphasis"].lower()
        assert "bachelor" in degree or "b.s" in degree or "science" in degree

    def test_gpa_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        assert "3.8" in items[0]["GPA"]

    def test_minor_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        assert "Mathematics" in items[0]["Minors"]

    def test_master_degree_recognised(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_MASTER)
        assert items
        degree = items[0]["Degree & Emphasis"].lower()
        assert "master" in degree or "m.s" in degree

    def test_output_keys_present(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_BACHELOR)
        required_keys = {"Institution", "Location", "Graduation Date",
                         "Degree & Emphasis", "GPA", "Minors", "Details"}
        assert required_keys.issubset(items[0].keys())

    def test_multi_education_returns_two_items(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_MULTI)
        assert len(items) == 2

    def test_multi_education_first_institution(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_MULTI)
        assert "State University" in items[0]["Institution"]

    def test_multi_education_second_institution(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_MULTI)
        assert "MIT" in items[1]["Institution"]

    def test_multi_education_both_dates_extracted(self, extractor):
        items = extractor.parse_education(EDUCATION_SECTION_MULTI)
        assert "2021" in items[0]["Graduation Date"]
        assert "2023" in items[1]["Graduation Date"]
