"""Unit tests for resume_parser.utils.text_normalizer."""

from resume_parser.utils.text_normalizer import normalize_whitespace


def test_none_returns_empty_string():
    assert normalize_whitespace(None) == ""


def test_empty_string_returns_empty():
    assert normalize_whitespace("") == ""


def test_whitespace_only_returns_empty():
    assert normalize_whitespace("   \n\n\t  ") == ""


def test_strips_trailing_spaces_per_line():
    result = normalize_whitespace("hello   \nworld   ")
    assert result == "hello\nworld"


def test_normalizes_windows_line_endings():
    result = normalize_whitespace("line one\r\nline two\r\nline three")
    assert result == "line one\nline two\nline three"


def test_normalizes_old_mac_line_endings():
    result = normalize_whitespace("line one\rline two\rline three")
    assert result == "line one\nline two\nline three"


def test_collapses_multiple_blank_lines_to_one():
    text = "first\n\n\n\nsecond"
    result = normalize_whitespace(text)
    assert result == "first\n\nsecond"


def test_single_blank_line_preserved():
    text = "first\n\nsecond"
    result = normalize_whitespace(text)
    assert result == "first\n\nsecond"


def test_strips_leading_and_trailing_blank_lines():
    text = "\n\nhello\n\n"
    result = normalize_whitespace(text)
    assert result == "hello"


def test_plain_text_unchanged():
    text = "Hello World"
    assert normalize_whitespace(text) == "Hello World"


def test_mixed_blank_and_content_lines():
    text = "a\n\nb\n\n\nc\n"
    result = normalize_whitespace(text)
    assert result == "a\n\nb\n\nc"


def test_preserves_internal_indentation():
    """Leading spaces within a non-empty line should be preserved."""
    text = "  indented line"
    result = normalize_whitespace(text)
    assert result == "indented line"
