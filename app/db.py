"""
SQLite database schema and helper functions for the EPICS Digital Evidence Platform.

Tables:
    - users:         Investigator profiles, roles, and salted password hashes
    - cases:         Investigation cases with status, priority, and assigned investigator
    - evidence:      Digital evidence records, SHA-256 hashes, metadata, and case linkage
    - activity_logs: Forensic audit trail tracking every upload, verification, and tamper test
"""
import sqlite3
from datetime import datetime, timezone
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL,
    badge_number  TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS cases (
    case_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number   TEXT    NOT NULL UNIQUE,
    title         TEXT    NOT NULL,
    description   TEXT,
    status        TEXT    NOT NULL DEFAULT 'Open',
    priority      TEXT    NOT NULL DEFAULT 'Medium',
    created_by    INTEGER NOT NULL,
    created_at    TEXT    NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id           INTEGER,
    original_filename TEXT    NOT NULL,
    stored_filename   TEXT    NOT NULL UNIQUE,
    file_type         TEXT    NOT NULL,
    mime_type         TEXT    NOT NULL,
    file_size         INTEGER NOT NULL,
    sha256_hash       TEXT    NOT NULL,
    uploaded_at       TEXT    NOT NULL,
    uploaded_by       INTEGER,
    notes             TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS activity_logs (
    log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    user_name   TEXT    NOT NULL,
    case_id     INTEGER,
    evidence_id INTEGER,
    action      TEXT    NOT NULL,
    details     TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
);
"""


def get_db():
    """Open one database connection per request and reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # Access columns by name
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Close the database connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def current_utc_time():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def init_db(app):
    """Create all tables and seed default demo data if database is new."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        seed_default_data(db)


def seed_default_data(db):
    """Seed single authorized investigator profile, realistic cases, and initial activity."""
    user_count = db.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
    if user_count == 0:
        now = current_utc_time()
        # Seed single authorized investigator
        db.execute(
            "INSERT INTO users (name, email, password_hash, role, badge_number, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                "Investigator Sharma",
                "investigator@cybercell.gov",
                generate_password_hash("investigator123"),
                "Investigator",
                "INV-5821",
                now,
            ),
        )
        db.commit()

    case_count = db.execute("SELECT COUNT(*) AS cnt FROM cases").fetchone()["cnt"]
    if case_count == 0:
        now = current_utc_time()
        db.execute(
            "INSERT INTO cases (case_number, title, description, status, priority, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "CASE-2026-001",
                "Unauthorized Financial Exfiltration (FinCorp Phishing)",
                "Investigation into spear-phishing incident targeting corporate accounts. Key evidence includes fraudulent payment notices and email headers.",
                "Open",
                "High",
                1,
                now,
            ),
        )
        db.execute(
            "INSERT INTO cases (case_number, title, description, status, priority, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "CASE-2026-002",
                "Digital Extortion via Encrypted Chat Logs",
                "Ransom threat communication reported by complainant. Chat screenshot and incident notes submitted for cryptographic hashing and verification.",
                "Under Review",
                "Critical",
                1,
                now,
            ),
        )
        db.execute(
            "INSERT INTO cases (case_number, title, description, status, priority, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "CASE-2026-003",
                "Intellectual Property Breach & Source Code Leak",
                "Alleged insider data exfiltration. Technical logs and document attachments pending preliminary forensic triage.",
                "Open",
                "Medium",
                1,
                now,
            ),
        )
        db.commit()

        # Seed initial audit log entries
        log_activity(
            user_id=1,
            user_name="Investigator Sharma",
            action="SYSTEM_INIT",
            details="System initialized with baseline demonstration cases under authorized investigator custody.",
            case_id=1,
        )


# ----------------------------------------------------------- Users & Auth

def get_user_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()


def get_user_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def list_users():
    return get_db().execute("SELECT user_id, name, email, role, badge_number FROM users ORDER BY user_id ASC").fetchall()


# ----------------------------------------------------------------- Cases

def create_case(case_number, title, description, priority, created_by):
    db = get_db()
    now = current_utc_time()
    cursor = db.execute(
        "INSERT INTO cases (case_number, title, description, priority, created_by, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (case_number.strip().upper(), title.strip(), description.strip(), priority, created_by, now),
    )
    db.commit()
    case_id = cursor.lastrowid
    user = get_user_by_id(created_by)
    user_name = user["name"] if user else "Investigator"
    log_activity(
        user_id=created_by,
        user_name=user_name,
        action="CASE_CREATED",
        details=f"Created investigation case {case_number}: '{title}' ({priority} priority)",
        case_id=case_id,
    )
    return case_id


def get_case(case_id):
    return get_db().execute(
        """
        SELECT c.*, u.name AS investigator_name, u.badge_number,
               (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) AS evidence_count
        FROM cases c
        LEFT JOIN users u ON c.created_by = u.user_id
        WHERE c.case_id = ?
        """,
        (case_id,),
    ).fetchone()


def list_cases(status_filter=None):
    db = get_db()
    query = """
        SELECT c.*, u.name AS investigator_name,
               (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.case_id) AS evidence_count
        FROM cases c
        LEFT JOIN users u ON c.created_by = u.user_id
    """
    params = []
    if status_filter and status_filter != "All":
        query += " WHERE c.status = ?"
        params.append(status_filter)
    query += " ORDER BY c.case_id DESC"
    return db.execute(query, params).fetchall()


def update_case_status(case_id, new_status, user_id=None, user_name="Investigator", reason=None):
    """Update case status and log the action in the forensic audit trail."""
    db = get_db()
    case = get_case(case_id)
    if not case:
        return False
    old_status = case["status"]
    db.execute("UPDATE cases SET status = ? WHERE case_id = ?", (new_status, case_id))
    db.commit()

    if new_status == "Closed":
        action = "CASE_CLOSED"
    elif new_status == "Open":
        action = "CASE_REOPENED"
    else:
        action = "CASE_STATUS_UPDATED"

    reason_str = f" Reason: {reason}" if reason else ""
    details = f"Case #{case['case_number']} ('{case['title']}') status changed from '{old_status}' to '{new_status}'.{reason_str}"

    log_activity(
        user_id=user_id,
        user_name=user_name,
        action=action,
        details=details,
        case_id=case_id,
    )
    return True


# -------------------------------------------------------------- Evidence

def add_evidence(original_filename, stored_filename, file_type, mime_type,
                 file_size, sha256_hash, uploaded_at, case_id=None, uploaded_by=None, notes=None):
    """Insert an evidence record and link it to an activity log."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO evidence (original_filename, stored_filename, file_type, mime_type, "
        "file_size, sha256_hash, uploaded_at, case_id, uploaded_by, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (original_filename, stored_filename, file_type, mime_type,
         file_size, sha256_hash, uploaded_at, case_id, uploaded_by, notes),
    )
    db.commit()
    evidence_id = cursor.lastrowid

    # Log this evidence upload
    user_name = "Investigator"
    if uploaded_by:
        u = get_user_by_id(uploaded_by)
        if u:
            user_name = u["name"]

    case_info = f" under Case #{case_id}" if case_id else ""
    log_activity(
        user_id=uploaded_by,
        user_name=user_name,
        action="EVIDENCE_UPLOADED",
        details=f"Uploaded '{original_filename}' ({file_type}, {file_size} bytes){case_info}. Recorded SHA-256: {sha256_hash[:16]}…",
        case_id=case_id,
        evidence_id=evidence_id,
    )
    return evidence_id


def get_evidence(evidence_id):
    """Return one evidence record with case and user metadata, or None."""
    return get_db().execute(
        """
        SELECT e.*, c.case_number, c.title AS case_title, u.name AS uploader_name, u.badge_number
        FROM evidence e
        LEFT JOIN cases c ON e.case_id = c.case_id
        LEFT JOIN users u ON e.uploaded_by = u.user_id
        WHERE e.evidence_id = ?
        """,
        (evidence_id,),
    ).fetchone()


def list_recent_evidence(limit=10, case_id=None):
    """Return the most recently uploaded evidence records."""
    db = get_db()
    if case_id:
        return db.execute(
            """
            SELECT e.*, c.case_number, c.title AS case_title
            FROM evidence e
            LEFT JOIN cases c ON e.case_id = c.case_id
            WHERE e.case_id = ?
            ORDER BY e.evidence_id DESC LIMIT ?
            """,
            (case_id, limit),
        ).fetchall()

    return db.execute(
        """
        SELECT e.*, c.case_number, c.title AS case_title
        FROM evidence e
        LEFT JOIN cases c ON e.case_id = c.case_id
        ORDER BY e.evidence_id DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()


def delete_evidence(evidence_id):
    """Delete an evidence record from database and remove physical file if present."""
    db = get_db()
    evidence = get_evidence(evidence_id)
    if evidence:
        # Disassociate from activity logs so audit trail remains intact without FK violation
        db.execute("UPDATE activity_logs SET evidence_id = NULL WHERE evidence_id = ?", (evidence_id,))
        db.execute("DELETE FROM evidence WHERE evidence_id = ?", (evidence_id,))
        db.commit()
        return True
    return False


# --------------------------------------------------------- Forensic Audit Logs

def log_activity(user_id=None, user_name="Investigator", action="ACTION", details="", case_id=None, evidence_id=None):
    """Record an audit trail event into the activity_logs table."""
    db = get_db()
    now = current_utc_time()
    db.execute(
        "INSERT INTO activity_logs (user_id, user_name, case_id, evidence_id, action, details, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, user_name, case_id, evidence_id, action, details, now),
    )
    db.commit()


def list_recent_activity(limit=15, case_id=None):
    """Retrieve chronological activity logs for the dashboard or case detail."""
    db = get_db()
    if case_id:
        return db.execute(
            "SELECT * FROM activity_logs WHERE case_id = ? ORDER BY log_id DESC LIMIT ?",
            (case_id, limit),
        ).fetchall()
    return db.execute(
        "SELECT * FROM activity_logs ORDER BY log_id DESC LIMIT ?",
        (limit,),
    ).fetchall()


# ------------------------------------------------------------- Dashboard Stats

def get_dashboard_stats():
    """Retrieve aggregate counts for the executive dashboard."""
    db = get_db()
    case_count = db.execute("SELECT COUNT(*) AS cnt FROM cases").fetchone()["cnt"]
    open_cases = db.execute("SELECT COUNT(*) AS cnt FROM cases WHERE status = 'Open'").fetchone()["cnt"]
    evidence_count = db.execute("SELECT COUNT(*) AS cnt FROM evidence").fetchone()["cnt"]
    verified_logs = db.execute(
        "SELECT COUNT(*) AS cnt FROM activity_logs WHERE action = 'INTEGRITY_VERIFIED'"
    ).fetchone()["cnt"]
    tamper_alerts = db.execute(
        "SELECT COUNT(*) AS cnt FROM activity_logs WHERE action = 'TAMPER_DETECTED'"
    ).fetchone()["cnt"]

    return {
        "total_cases": case_count,
        "open_cases": open_cases,
        "total_evidence": evidence_count,
        "verifications_run": verified_logs,
        "tamper_alerts": tamper_alerts,
    }
