# Review 1 Prototype: Test Report

**Component tested:** Forensic Evidence Management, Cryptographic SHA-256 Hashing, Verification, Officer Authentication, Case Management, and Forensic Audit Logs
**Date of test run:** 22 November 2026
**Environment:** Windows 11, Python 3.13.1, Flask 3.1.2, pytest 8.3.4
**Test data:** synthetic files only (see `sample_evidence/README.md`)

---

## 1. Automated Tests Summary (pytest)

Command: `.\.venv\Scripts\python.exe -m pytest -v`
Result: **40 passed, 0 failed (100% Pass Rate).**

### Suite Breakdown:

#### A. New Foundation & Review 2 Sneak-Peek Features (`tests/test_features_revised.py` - 13 Tests)
| Test Name | What it verifies | Status |
|---|---|---|
| `test_seed_users_and_cases_exist` | Database auto-initializes with demo investigator and baseline cases | PASSED |
| `test_login_success_and_logout` | Secure password check, session creation, flash notice, and clean logout | PASSED |
| `test_unauthenticated_access_redirects_to_login` | Strict route guarding: unauthenticated access redirects to login | PASSED |
| `test_login_invalid_credentials` | Rejection of bad passwords with descriptive error message | PASSED |
| `test_switch_user_profile` | 1-click fast login profile authentication | PASSED |
| `test_cases_listing_and_filter` | Case listing and filtering by status (Open, Under Review, Closed) | PASSED |
| `test_create_new_case` | Case registration, unique case number enforcement, audit trail creation | PASSED |
| `test_upload_evidence_with_case_link` | Ingesting digital evidence attached directly to an active investigation case | PASSED |
| `test_activity_log_page` | Chronological chain-of-custody audit log rendering | PASSED |
| `test_delete_evidence_record` | Clean deletion of evidence records with foreign key cascade handling | PASSED |
| `test_upload_docx_file_accepted` | Secure upload and magic-byte validation of modern DOCX documents | PASSED |
| `test_upload_doc_file_accepted` | Secure upload and magic-byte validation of legacy DOC documents | PASSED |
| `test_close_and_reopen_case_with_audit_trail` | Closing open cases and re-opening closed cases with immutable audit trail logging | PASSED |

#### B. Cryptographic Integrity Core (`tests/test_integrity.py` - 10 Tests)
| Test Name | What it verifies | Status |
|---|---|---|
| `test_hash_matches_known_test_vector` | SHA-256("abc") matches published NIST test vector | PASSED |
| `test_hash_of_empty_file` | SHA-256 of empty file equals NIST standard | PASSED |
| `test_hash_is_64_lowercase_hex_characters` | Valid 64-character hexadecimal format | PASSED |
| `test_large_file_is_hashed_correctly_in_chunks` | Chunked 64KB hashing equals full-file hash | PASSED |
| `test_one_byte_change_gives_a_different_hash` | Avalanche effect: single changed bit alters entire hash | PASSED |
| `test_verify_unchanged_file_returns_match` | Unaltered stored file returns MATCH | PASSED |
| `test_verify_accepts_uppercase_recorded_hash` | Case-insensitive hash comparison | PASSED |
| `test_verify_modified_file_returns_mismatch` | Modified file returns MISMATCH | PASSED |
| `test_verify_missing_file_returns_missing` | Missing file handled cleanly with MISSING status | PASSED |
| `test_tampered_copy_is_detected_and_original_is_unchanged` | Modified copy flagged as MISMATCH while original remains MATCH | PASSED |

#### C. Route Security & Input Validation (`tests/test_routes.py` - 17 Tests)
| Test Name | What it verifies | Status |
|---|---|---|
| `test_index_page_loads` | Executive dashboard and intake portal load (HTTP 200) | PASSED |
| `test_valid_upload_calculates_and_displays_hash` | Valid file upload calculates hash and displays metadata | PASSED |
| `test_uploaded_file_is_stored_unchanged` | Bytes on disk match upload byte-for-byte | PASSED |
| `test_uppercase_extension_is_accepted` | Uppercase extensions (e.g. .PNG) accepted | PASSED |
| `test_no_file_part_is_rejected` | Empty upload request rejected | PASSED |
| `test_empty_filename_is_rejected` | No-selection submit rejected | PASSED |
| `test_disallowed_extension_is_rejected` | Executable/binary files (.exe) rejected | PASSED |
| `test_file_without_extension_is_rejected` | Extensionless files rejected | PASSED |
| `test_zero_byte_file_is_rejected` | Empty (0 byte) files rejected | PASSED |
| `test_content_not_matching_extension_is_rejected` | Renamed files failing magic-byte check rejected | PASSED |
| `test_path_traversal_filename_is_saved_safely` | Path traversal attacks (`../../evil.txt`) sanitized | PASSED |
| `test_oversized_file_is_rejected` | Files exceeding 16 MB limit rejected | PASSED |
| `test_verify_unchanged_file_shows_match` | MATCH badge and verification notice displayed | PASSED |
| `test_verify_modified_file_shows_mismatch` | MISMATCH badge and warning displayed | PASSED |
| `test_verify_deleted_file_shows_missing` | Missing file error displayed gracefully | PASSED |
| `test_tamper_test_detects_change_and_preserves_original` | Demonstration of copy tampering without altering original | PASSED |
| `test_unknown_evidence_id_redirects_with_message` | Non-existent evidence ID redirects safely | PASSED |

---

## 2. Live Verification Matrix

| # | Action | Expected Output | Observed Output | Result |
|---|---|---|---|---|
| 1 | Officer Login | Authenticates with `investigator@cybercell.gov` | Welcome badge, officer role, session active | PASS |
| 2 | Case Creation | Creates `CASE-2026-004` | Case appears in case list with priority badge | PASS |
| 3 | Ingest Evidence | Upload PDF attached to Case | SHA-256 hash calculated, linked in case dossier | PASS |
| 4 | Terminal Cross-Check | Run `Get-FileHash` | Matches platform recorded hash 100% | PASS |
| 5 | Verify Integrity | Click "Verify integrity" | Emerald MATCH status displayed | PASS |
| 6 | Tamper Demonstration | Click "Run tamper test on a copy" | Copy = MISMATCH, Original = MATCH | PASS |
| 7 | Audit Trail | Inspect `/activity` | Shows USER_LOGIN, CASE_CREATED, EVIDENCE_UPLOADED, INTEGRITY_VERIFIED | PASS |
| 8 | Content Preview | View image evidence | Inline image renders in browser | PASS |
| 9 | Word Document Ingestion | Upload synthetic `.docx` & `.doc` | File accepted, magic byte confirmed, SHA-256 computed | PASS |
| 10 | Case Close & Re-open | Click "Close Case" / "Re-open Case" in dossier | Status toggles, audited with `CASE_CLOSED` and `CASE_REOPENED` | PASS |
| 11 | Evidence Removal | Click "Delete Record" on missing/orphaned file | Record removed cleanly from DB and interface | PASS |
