"""Unit tests for resume_parser.utils.section_finder."""

from resume_parser.utils.section_finder import find_section


SAMPLE_RESUME = """\
Summary
Results-driven engineer with 5 years of experience.

Experience
Acme Corp | Software Engineer | Jan 2020 - Present
Built distributed systems.

Education
State University, B.S. Computer Science, 2019

Skills
Python, Go, SQL
"""


class TestFindSection:
    def test_extracts_summary_section(self):
        result = find_section(SAMPLE_RESUME, ["summary"], ["experience", "education"])
        assert "Results-driven" in result
        assert "Acme Corp" not in result

    def test_extracts_experience_section(self):
        result = find_section(SAMPLE_RESUME, ["experience"], ["education", "skills"])
        assert "Acme Corp" in result
        assert "State University" not in result

    def test_extracts_education_section(self):
        result = find_section(SAMPLE_RESUME, ["education"], ["skills"])
        assert "State University" in result
        assert "Acme Corp" not in result

    def test_returns_empty_for_missing_section(self):
        result = find_section(SAMPLE_RESUME, ["certifications"], ["skills"])
        assert result == ""

    def test_empty_text_returns_empty(self):
        assert find_section("", ["summary"], ["experience"]) == ""

    def test_none_text_returns_empty(self):
        assert find_section(None, ["summary"], ["experience"]) == ""

    def test_section_at_end_of_document(self):
        """Section with no trailing end keyword should capture to EOF."""
        result = find_section(SAMPLE_RESUME, ["skills"], ["nonexistent"])
        assert "Python" in result

    def test_case_insensitive_matching(self):
        text = "EXPERIENCE\nAcme Corp\n\nEDUCATION\nState University"
        result = find_section(text, ["experience"], ["education"])
        assert "Acme Corp" in result
        assert "State University" not in result

    def test_inline_section_fallback(self):
        """When the section header is inline (not on its own line), use fallback."""
        text = "Summary: Passionate engineer.\nExperience: 5 years."
        result = find_section(text, ["summary"], ["experience"])
        assert "Passionate" in result

    def test_first_of_multiple_start_keywords_used(self):
        """Multiple start alternatives — first matching one should be used."""
        text = "Profile\nMy profile text.\n\nExperience\nJob stuff."
        result = find_section(text, ["profile", "summary"], ["experience"])
        assert "My profile text" in result
        assert "Job stuff" not in result
