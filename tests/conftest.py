import warnings
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
DATA_DIR = TESTS_DIR / "data"


@pytest.fixture(scope="session")
def fake_resume_path() -> Path:
    """Provide the path to the sample resume used across tests."""
    return DATA_DIR / "fake_resumes" / "fake_resume.pdf"


@pytest.fixture(scope="session")
def fake_job_description_path() -> Path:
    """Provide the path to the sample job description used across tests."""
    return DATA_DIR / "job_descriptions" / "sample_job.txt"


@pytest.fixture(autouse=True, scope="session")
def suppress_pytesseract_find_loader_deprecation():
    """Silence deprecated pkgutil.find_loader usage from pytesseract."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=".*pkgutil\\.find_loader.*",
            module="pytesseract.pytesseract",
        )
        yield
