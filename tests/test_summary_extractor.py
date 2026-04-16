# pylint: disable=redefined-outer-name
"""Unit tests for resume_parser.extractors.summary_extractor.SummaryExtractor."""

import pytest
from resume_parser.extractors.summary_extractor import SummaryExtractor


@pytest.fixture()
def extractor():
    return SummaryExtractor()


def _write_resume(tmp_path, content: str):
    """Write resume text to a temp .txt file and return its path string."""
    p = tmp_path / "resume.txt"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestSummaryExtractorFromFakePDF:
    """Integration test using the bundled fake resume PDF."""

    def test_extract_returns_dict_with_section_key(self, fake_resume_path, extractor):
        result = extractor.extract(str(fake_resume_path))
        assert isinstance(result, dict)
        assert "section" in result

    def test_extract_section_is_string(self, fake_resume_path, extractor):
        result = extractor.extract(str(fake_resume_path))
        assert isinstance(result["section"], str)

    def test_extract_section_not_empty(self, fake_resume_path, extractor):
        result = extractor.extract(str(fake_resume_path))
        assert result["section"].strip(), "Summary section should not be empty"


class TestSummaryExtractorFromText:
    """Fast unit tests using in-memory text files."""

    def test_extracts_summary_section(self, tmp_path, extractor):
        content = (
            "Summary\n"
            "Experienced data engineer with 7 years in cloud infrastructure.\n\n"
            "Experience\n"
            "Acme Corp\n"
        )
        result = extractor.extract(_write_resume(tmp_path, content))
        assert "data engineer" in result["section"]

    def test_returns_empty_section_when_no_summary(self, tmp_path, extractor):
        content = "Experience\nAcme Corp\n\nEducation\nState University\n"
        result = extractor.extract(_write_resume(tmp_path, content))
        assert result["section"] == "" or "Acme" not in result["section"]

    def test_profile_keyword_is_recognised(self, tmp_path, extractor):
        content = (
            "Profile\n"
            "Passionate developer focused on open-source tooling.\n\n"
            "Skills\n"
            "Python, Go\n"
        )
        result = extractor.extract(_write_resume(tmp_path, content))
        assert "Passionate developer" in result["section"]

    def test_objective_keyword_is_recognised(self, tmp_path, extractor):
        content = (
            "Objective\n"
            "Seeking a senior role in ML engineering.\n\n"
            "Experience\n"
            "Some Company\n"
        )
        result = extractor.extract(_write_resume(tmp_path, content))
        assert "senior role" in result["section"]

    def test_professional_summary_keyword_is_recognised(self, tmp_path, extractor):
        content = (
            "Professional Summary\n"
            "Full-stack engineer with React and Django expertise.\n\n"
            "Education\n"
            "MIT\n"
        )
        result = extractor.extract(_write_resume(tmp_path, content))
        assert "Full-stack" in result["section"]

    def test_summary_does_not_bleed_into_next_section(self, tmp_path, extractor):
        content = (
            "Summary\n"
            "Brief about me.\n\n"
            "Experience\n"
            "Job content here.\n"
        )
        result = extractor.extract(_write_resume(tmp_path, content))
        assert "Job content" not in result["section"]
