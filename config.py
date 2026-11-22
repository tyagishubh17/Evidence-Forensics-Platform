"""
Application configuration.

Secrets are read from environment variables and are never written in source
code. See .env.example for the variables the project uses.
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Used by Flask to sign session data (flash messages). If no SECRET_KEY
    # environment variable is set, a random key is generated at start-up,
    # which is fine for local development.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    # Original uploaded evidence files. These are never modified.
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")

    # Modified copies created by the tamper-detection demonstration.
    # Kept in a separate folder so they can never be confused with evidence.
    TEST_COPY_FOLDER = os.path.join(BASE_DIR, "app", "test_copies")

    # SQLite database file that stores evidence metadata and original hashes.
    DATABASE = os.path.join(BASE_DIR, "instance", "evidence.db")

    # Reject uploads larger than 16 MB.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Only these file types may be uploaded.
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "jpeg", "png", "txt"}

    # Planned for later reviews (not used by the Review 1 prototype):
    # GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
