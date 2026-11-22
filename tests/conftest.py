import os
import sys

import pytest

# Make the project root importable (for `app` and `config`).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    """An app that uses temporary folders, so tests never touch real data."""
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-only-key",
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        "TEST_COPY_FOLDER": str(tmp_path / "test_copies"),
        "DATABASE": str(tmp_path / "test.db"),
    })


@pytest.fixture
def client(app):
    c = app.test_client()
    with c.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Investigator Sharma"
        sess["user_role"] = "Investigator"
        sess["badge_number"] = "INV-5821"
    return c


@pytest.fixture
def unauth_client(app):
    return app.test_client()
