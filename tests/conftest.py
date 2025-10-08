"""
Pytest fixture for loading fake resume files.

This fixture automatically parameterizes tests with all resume files in
`tests/data/fake_resumes`. Each test run gets one file path.
"""

from pathlib import Path
import pytest

# Pick the extension(s) you actually want
EXTENSIONS = ("*.pdf", "*.txt")

@pytest.fixture(
    params=[
        path
        for pattern in EXTENSIONS
        for path in (Path(__file__).parent / "data" / "fake_resumes").glob(pattern)
    ]
)
def fake_resume_path(request):
    """
    Yields one fake resume path for each test run.
    """
    return request.param


@pytest.fixture
def fake_job_description_path():
    """
    Provides a sample job description path for tests.
    """
    return Path(__file__).parent / "data" / "job_descriptions" / "sample_job.txt"
