import pytest
from pathlib import Path


@pytest.fixture
def test_folder():
    return Path(__file__).parent
