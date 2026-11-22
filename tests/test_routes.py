"""End-to-end tests of the Flask routes using Flask's test client."""
import hashlib
import io
import os

from app import create_app

TXT_CONTENT = b"Synthetic incident note for testing. No real data.\n"
PNG_CONTENT = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32  # PNG signature + filler bytes
PDF_CONTENT = b"%PDF-1.4\n% synthetic test pdf\n"


def upload(client, content, filename, follow=True):
    return client.post(
        "/upload",
        data={"evidence_file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
        follow_redirects=follow,
    )


def stored_files(app):
    return os.listdir(app.config["UPLOAD_FOLDER"])


def upload_and_get_record(app, client, content=TXT_CONTENT, filename="note.txt"):
    upload(client, content, filename)
    with app.app_context():
        from app.db import list_recent_evidence
        return dict(list_recent_evidence(1)[0])


# ------------------------------------------------------------ upload page

def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Upload evidence" in response.data


def test_valid_upload_calculates_and_displays_hash(app, client):
    response = upload(client, TXT_CONTENT, "incident_note.txt")
    expected_hash = hashlib.sha256(TXT_CONTENT).hexdigest()

    assert response.status_code == 200
    assert b"SHA-256 hash calculated and recorded" in response.data
    assert expected_hash.encode() in response.data
    assert b"incident_note.txt" in response.data
    assert b"Plain text" in response.data


def test_uploaded_file_is_stored_unchanged(app, client):
    record = upload_and_get_record(app, client, PDF_CONTENT, "report.pdf")
    path = os.path.join(app.config["UPLOAD_FOLDER"], record["stored_filename"])

    assert open(path, "rb").read() == PDF_CONTENT
    assert record["sha256_hash"] == hashlib.sha256(PDF_CONTENT).hexdigest()
    assert record["file_size"] == len(PDF_CONTENT)
    assert record["mime_type"] == "application/pdf"


def test_uppercase_extension_is_accepted(app, client):
    response = upload(client, PNG_CONTENT, "SCREENSHOT.PNG")
    assert b"PNG image" in response.data
    assert len(stored_files(app)) == 1


# ------------------------------------------------------- invalid uploads

def test_no_file_part_is_rejected(app, client):
    response = client.post("/upload", data={}, follow_redirects=True)
    assert b"No file was selected" in response.data
    assert stored_files(app) == []


def test_empty_filename_is_rejected(app, client):
    response = upload(client, b"", "")
    assert b"No file was selected" in response.data
    assert stored_files(app) == []


def test_disallowed_extension_is_rejected(app, client):
    response = upload(client, b"MZ fake program", "tool.exe")
    assert b"not an allowed file type" in response.data
    assert stored_files(app) == []


def test_file_without_extension_is_rejected(app, client):
    response = upload(client, b"data", "README")
    assert b"not an allowed file type" in response.data
    assert stored_files(app) == []


def test_zero_byte_file_is_rejected(app, client):
    response = upload(client, b"", "empty.txt")
    assert b"is empty (0 bytes)" in response.data
    assert stored_files(app) == []


def test_content_not_matching_extension_is_rejected(app, client):
    response = upload(client, b"just plain text", "fake.pdf")
    assert b"do not look like a valid .pdf file" in response.data
    assert stored_files(app) == []


def test_path_traversal_filename_is_saved_safely(app, client, tmp_path):
    record = upload_and_get_record(app, client, TXT_CONTENT, "../../evil.txt")

    # Display name is reduced to the base name; storage name is server-generated.
    assert record["original_filename"] == "evil.txt"
    assert ".." not in record["stored_filename"]
    assert stored_files(app) == [record["stored_filename"]]
    assert not (tmp_path / "evil.txt").exists()


def test_oversized_file_is_rejected():
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        small_app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-key",
            "UPLOAD_FOLDER": os.path.join(folder, "uploads"),
            "TEST_COPY_FOLDER": os.path.join(folder, "copies"),
            "DATABASE": os.path.join(folder, "test.db"),
            "MAX_CONTENT_LENGTH": 1024,
        })
        c = small_app.test_client()
        with c.session_transaction() as sess:
            sess["user_id"] = 1
        response = upload(c, b"a" * 4096, "big.txt")
        assert b"The file is too large" in response.data
        assert os.listdir(small_app.config["UPLOAD_FOLDER"]) == []


# ----------------------------------------------------------- verification

def test_verify_unchanged_file_shows_match(app, client):
    record = upload_and_get_record(app, client)
    response = client.post(f"/evidence/{record['evidence_id']}/verify")
    assert response.status_code == 200
    assert b"status-match" in response.data
    assert b"The stored file is unchanged" in response.data


def test_verify_modified_file_shows_mismatch(app, client):
    record = upload_and_get_record(app, client)
    # Simulate tampering with the stored file (temporary test folder only).
    path = os.path.join(app.config["UPLOAD_FOLDER"], record["stored_filename"])
    with open(path, "ab") as f:
        f.write(b"x")

    response = client.post(f"/evidence/{record['evidence_id']}/verify")
    assert b"status-mismatch" in response.data
    assert b"has changed since it was uploaded" in response.data


def test_verify_deleted_file_shows_missing(app, client):
    record = upload_and_get_record(app, client)
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], record["stored_filename"]))

    response = client.post(f"/evidence/{record['evidence_id']}/verify")
    assert b"status-missing" in response.data
    assert b"could not be found" in response.data


def test_tamper_test_detects_change_and_preserves_original(app, client):
    record = upload_and_get_record(app, client, PDF_CONTENT, "statement.pdf")
    original_path = os.path.join(app.config["UPLOAD_FOLDER"], record["stored_filename"])

    response = client.post(f"/evidence/{record['evidence_id']}/tamper-test")
    html = response.data.decode()

    # The copy is flagged as MISMATCH and the original as MATCH.
    assert response.status_code == 200
    assert "status-mismatch" in html
    assert "status-match" in html
    assert "The original evidence file still matches" in html

    # The copy was written to the separate test-copies folder only.
    copies = os.listdir(app.config["TEST_COPY_FOLDER"])
    assert len(copies) == 1 and "_tampered_copy" in copies[0]
    assert stored_files(app) == [record["stored_filename"]]

    # The original evidence file is byte-for-byte unchanged.
    assert open(original_path, "rb").read() == PDF_CONTENT


def test_unknown_evidence_id_redirects_with_message(client):
    response = client.get("/evidence/999", follow_redirects=True)
    assert b"Evidence record #999 was not found" in response.data

    response = client.post("/evidence/999/verify", follow_redirects=True)
    assert b"Evidence record #999 was not found" in response.data
