import os
import pytest

def pytest_configure(config):
    """Set test env before importing application modules."""
    os.environ["ICT_DISABLE_LOG_ROTATION"] = "1"

def pytest_unconfigure(config):
    os.environ.pop("ICT_DISABLE_LOG_ROTATION", None)

@pytest.fixture(autouse=True)
def disable_log_rotation():
    """Ensure env is present inside each test too."""
    os.environ["ICT_DISABLE_LOG_ROTATION"] = "1"
    yield
