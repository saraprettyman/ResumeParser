"""Unit tests for resume_parser.utils.regex_helpers."""

from resume_parser.utils.regex_helpers import (
    find_first,
    find_all,
    safe_search,
    find_additional_urls,
)


# ---------------------------------------------------------------------------
# find_first
# ---------------------------------------------------------------------------

class TestFindFirst:
    def test_returns_first_match(self):
        assert find_first(r"\d+", "abc 42 xyz 99") == "42"

    def test_returns_none_when_no_match(self):
        assert find_first(r"\d+", "no digits here") is None

    def test_case_insensitive_by_default(self):
        assert find_first(r"hello", "HELLO world") == "HELLO"

    def test_strips_surrounding_whitespace(self):
        result = find_first(r"\s*\w+\s*", "  hello  world")
        assert result == result.strip()

    def test_returns_full_match(self):
        pattern = r"[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+"
        assert find_first(pattern, "user@example.com") == "user@example.com"


# ---------------------------------------------------------------------------
# find_all
# ---------------------------------------------------------------------------

class TestFindAll:
    def test_single_pattern_multiple_matches(self):
        result = find_all([r"\d+"], "a1 b2 c3")
        assert result == ["1", "2", "3"]

    def test_multiple_patterns_combined(self):
        result = find_all([r"\d+", r"[A-Z]+"], "abc 42 XYZ")
        assert "42" in result
        assert "XYZ" in result

    def test_empty_text_returns_empty(self):
        assert not find_all([r"\d+"], "")

    def test_no_match_returns_empty(self):
        assert not find_all([r"\d+"], "no numbers")


# ---------------------------------------------------------------------------
# safe_search
# ---------------------------------------------------------------------------

class TestSafeSearch:
    def test_returns_true_on_match(self):
        assert safe_search(r"\d+", "abc 42") is True

    def test_returns_false_on_no_match(self):
        assert safe_search(r"\d+", "no digits") is False

    def test_case_insensitive_by_default(self):
        assert safe_search(r"python", "I love Python") is True

    def test_empty_text_returns_false(self):
        assert safe_search(r"\w+", "") is False


# ---------------------------------------------------------------------------
# find_additional_urls
# ---------------------------------------------------------------------------

class TestFindAdditionalUrls:
    def test_excludes_known_urls(self):
        text = "Visit https://github.com/user and https://example.com"
        known = ["https://github.com/user"]
        result = find_additional_urls(text, known)
        assert "https://example.com" in result
        assert not any("github.com/user" in u for u in result)

    def test_known_urls_empty_returns_all(self):
        text = "See https://example.com for details"
        result = find_additional_urls(text, [])
        assert any("example.com" in u for u in result)

    def test_trailing_slash_treated_as_same_url(self):
        text = "See https://example.com/ for details"
        known = ["https://example.com"]
        result = find_additional_urls(text, known)
        assert result == []

    def test_no_urls_in_text_returns_empty(self):
        assert not find_additional_urls("plain text no urls", [])

    def test_www_url_detected(self):
        text = "Go to www.example.com for info"
        result = find_additional_urls(text, [])
        assert any("example.com" in u for u in result)

    def test_none_known_urls_ignored(self):
        """None entries in known_urls should not cause errors."""
        text = "Visit https://example.com"
        result = find_additional_urls(text, [None, "https://other.com"])
        assert any("example.com" in u for u in result)
