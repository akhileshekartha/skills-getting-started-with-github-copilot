import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


# Take a deep copy of the original in-memory activities so we can
# restore them before each test and keep tests isolated.
_original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities store before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))
    yield


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client bound to the main application."""
    return TestClient(app_module.app)
