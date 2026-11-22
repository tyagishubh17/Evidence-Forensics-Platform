"""Tests for enhanced Review 1 / Review 2 foundation features (Auth, Cases, Activity Logs)."""
import io
import os
import pytest
from app.db import get_user_by_email, list_cases, list_recent_activity


def test_seed_users_and_cases_exist(app):
    with app.app_context():
        user = get_user_by_email("investigator@cybercell.gov")
        assert user is not None
        assert user["name"] == "Investigator Sharma"
        assert user["role"] == "Investigator"
        assert user["badge_number"] == "INV-5821"

        cases = list_cases()
        assert len(cases) >= 3
        case_numbers = [c["case_number"] for c in cases]
        assert "CASE-2026-001" in case_numbers


def test_login_success_and_logout(client):
    # GET login page
    res = client.get("/login")
    assert res.status_code == 200
    assert b"Aegis Forensics Portal" in res.data
    assert b"Investigator Sharma" in res.data

    # POST login valid credentials
    res = client.post("/login", data={
        "email": "investigator@cybercell.gov",
        "password": "investigator123"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, Investigator Sharma" in res.data

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"signed out successfully" in res.data

    # After logout, accessing dashboard must block and redirect to /login!
    res = client.get("/", follow_redirects=True)
    assert res.status_code == 200
    assert b"Authentication required" in res.data
    assert b"Investigator Sign In" in res.data


def test_unauthenticated_access_redirects_to_login(unauth_client):
    res = unauth_client.get("/", follow_redirects=True)
    assert res.status_code == 200
    assert b"Authentication required" in res.data
    assert b"Investigator Sign In" in res.data

    res_cases = unauth_client.get("/cases", follow_redirects=True)
    assert res_cases.status_code == 200
    assert b"Authentication required" in res_cases.data


def test_login_invalid_credentials(client):
    res = client.post("/login", data={
        "email": "investigator@cybercell.gov",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid credentials" in res.data


def test_switch_user_profile(client):
    res = client.get("/switch-user/1", follow_redirects=True)
    assert res.status_code == 200
    assert b"Investigator Sharma" in res.data


def test_cases_listing_and_filter(client):
    res = client.get("/cases")
    assert res.status_code == 200
    assert b"CASE-2026-001" in res.data

    # Filter Open
    res = client.get("/cases?status=Open")
    assert res.status_code == 200
    assert b"CASE-2026-001" in res.data


def test_create_new_case(app, client):
    res = client.post("/cases/new", data={
        "case_number": "CASE-2026-999",
        "title": "Suspected Ransomware Incident",
        "description": "Lockbit payload detected on finance server.",
        "priority": "Critical"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"CASE-2026-999" in res.data
    assert b"Suspected Ransomware Incident" in res.data

    with app.app_context():
        logs = list_recent_activity(5)
        actions = [log["action"] for log in logs]
        assert "CASE_CREATED" in actions


def test_upload_evidence_with_case_link(app, client):
    content = b"Case-linked synthetic evidence document.\n"
    res = client.post("/upload", data={
        "evidence_file": (io.BytesIO(content), "case_evidence.txt"),
        "case_id": "1",
        "notes": "Recovered from flash drive"
    }, content_type="multipart/form-data", follow_redirects=True)

    assert res.status_code == 200
    assert b"case_evidence.txt" in res.data
    assert b"CASE-2026-001" in res.data


def test_activity_log_page(client):
    res = client.get("/activity")
    assert res.status_code == 200
    assert b"Forensic Activity & Chain of Custody Log" in res.data


def test_delete_evidence_record(app, client):
    content = b"File to be deleted.\n"
    res = client.post("/upload", data={
        "evidence_file": (io.BytesIO(content), "to_delete.txt"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200
    assert b"to_delete.txt" in res.data

    with app.app_context():
        from app.db import list_recent_evidence
        latest = list_recent_evidence(1)[0]
        ev_id = latest["evidence_id"]

    # Delete record
    res = client.post(f"/evidence/{ev_id}/delete", follow_redirects=True)
    assert res.status_code == 200
    assert b"was successfully removed" in res.data


def test_upload_docx_file_accepted(app, client):
    docx_content = b"PK\x03\x04" + b"\x00" * 30
    res = client.post("/upload", data={
        "evidence_file": (io.BytesIO(docx_content), "briefing.docx"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200
    assert b"briefing.docx" in res.data
    assert b"Word document (.docx)" in res.data


def test_upload_doc_file_accepted(app, client):
    doc_content = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 30
    res = client.post("/upload", data={
        "evidence_file": (io.BytesIO(doc_content), "legacy_memo.doc"),
    }, content_type="multipart/form-data", follow_redirects=True)
    assert res.status_code == 200
    assert b"legacy_memo.doc" in res.data
    assert b"Word document (.doc)" in res.data


def test_close_and_reopen_case_with_audit_trail(app, client):
    # 1. Close case 1
    res = client.post("/cases/1/status", data={
        "status": "Closed",
        "reason": "Investigation concluded, evidence documented."
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"has been CLOSED" in res.data
    assert b"Closed" in res.data
    assert b"Re-open Case" in res.data

    with app.app_context():
        from app.db import get_case, list_recent_activity
        case = get_case(1)
        assert case["status"] == "Closed"

        activity = list_recent_activity(5, case_id=1)
        actions = [a["action"] for a in activity]
        assert "CASE_CLOSED" in actions
        assert any("Investigation concluded" in (a["details"] or "") for a in activity)

    # 2. Re-open case 1
    res2 = client.post("/cases/1/status", data={
        "status": "Open",
        "reason": "New supplemental evidence submitted for analysis."
    }, follow_redirects=True)
    assert res2.status_code == 200
    assert b"has been RE-OPENED" in res2.data
    assert b"Open" in res2.data
    assert b"Close Case" in res2.data

    with app.app_context():
        case = get_case(1)
        assert case["status"] == "Open"

        activity = list_recent_activity(5, case_id=1)
        actions = [a["action"] for a in activity]
        assert "CASE_REOPENED" in actions
        assert any("New supplemental evidence" in (a["details"] or "") for a in activity)

