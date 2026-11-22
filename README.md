# AI-Driven Digital Evidence Management and Preliminary Analysis Platform

An **EPICS (Engineering Projects in Community Service)** academic project: a web-based digital forensics platform to help investigators organize digital evidence, preserve evidentiary integrity with cryptographic SHA-256 hashes, maintain chain-of-custody audit logs, and prepare structured preliminary case reports.

> **Current Stage: Review 1 (Enhanced Foundation & Initial Prototype)**
> 
> This repository contains the complete Review 1 deliverables: comprehensive project documentation, system architecture diagrams, database ER models, workflow specifications, UI wireframes, plus an **expanded, high-fidelity working prototype** featuring:
> 1. **Officer Authentication & Session Management** (with 1-click supervisor demo profiles).
> 2. **Investigation Case Management** (Case registration, status/priority tagging, and case dossiers).
> 3. **Cryptographic Evidence Ingestion** (SHA-256 hashing, safe UUID storage, metadata recording).
> 4. **Live Integrity Verification** (Real-time recalculation: MATCH vs. MISMATCH).
> 5. **Controlled Tamper Detection Demonstration** (Demonstrates hash divergence on an isolated copy while preserving original evidence).
> 6. **Forensic Chain-of-Custody Audit Trail** (Tracking every intake, verification, and tamper check).
> 7. **Preliminary Content Preview** (Review 2 sneak-peek: image rendering and plain-text inspection).
> 
> *Academic EPICS prototype developed for authorized investigative training with synthetic sample data only.*

---

## Repository Structure

```
├── app/
│   ├── __init__.py          Flask application factory
│   ├── routes.py            Auth, Dashboard, Cases, Evidence, Verification & Audit routes
│   ├── integrity.py         SHA-256 hashing, verification, tamper-test copy (pure Python)
│   ├── db.py                SQLite models (users, cases, evidence, activity_logs) + auto-seeding
│   ├── templates/           base.html, login.html, index.html, cases.html, case_detail.html, evidence.html, activity.html
│   ├── static/css|js/       Modern Forensic Theme (style.css), local Bootstrap 5, upload.js
│   ├── uploads/             Original evidence files (runtime, git-ignored, UUID-isolated)
│   └── test_copies/         Tamper-demo copies (runtime, git-ignored, separate from evidence)
├── docs/                    Review 1 documentation, diagrams, wireframes, test report
├── sample_evidence/         Synthetic sample files for demonstration (PDF, PNG, DOCX, TXT, invalid)
├── tests/                   Automated pytest test suite (40 tests covering all routes, features, and cryptographic logic)
├── instance/                SQLite database (auto-created at runtime, git-ignored)
├── config.py                Settings (file limits, allowed extensions, session configuration)
├── run.py                   Application entry point
├── requirements.txt         Python dependencies
└── README.md
```

---

## Setup & Quick Start

Requirements: **Python 3.10+** (tested with Python 3.13) and Git.

### 1. Environment Setup

**Windows (PowerShell)**
```powershell
git clone <repository-url>
cd <repository-folder>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**
```bash
git clone <repository-url>
cd <repository-folder>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Application Server

```bash
python run.py
```
Open your browser to: **http://127.0.0.1:5000**

---

## Authorized Access & Investigator Profile

The system uses a single authorized user role (**Investigator**) for handling cases and digital evidence:

| Role | Officer / User Name | Email | Password | Badge Number |
|---|---|---|---|---|
| **Investigator** | Investigator Sharma | `investigator@cybercell.gov` | `investigator123` | `INV-5821` |

> *Quick Demo Access:* On the `/login` screen, click the **1-Click Fast Login** button to immediately enter the dashboard without typing credentials during presentations.

---

## Demonstration Walkthrough for Review 1 (5 Minutes)

Follow this step-by-step procedure to present the working prototype to supervisors:

1. **Executive Dashboard Overview:**
   - Open `http://127.0.0.1:5000`.
   - Point out the 4 Stat Cards: Active Cases, Evidence Files, Hashes Verified, Tamper Alerts.
   - Show the officer badge in the navigation bar (`Inspector Rajesh Sharma · Lead Investigator`).
2. **Investigation Case Management:**
   - Click **Cases** in the top navigation.
   - Show the pre-seeded active cases (e.g. `CASE-2026-001: Unauthorized Financial Exfiltration`).
   - Click **Create New Case** to register a new case (e.g. `CASE-2026-004: Ransom Threat Letter`, Priority: `Critical`).
   - Open a case dossier to view linked digital evidence and case-specific activity.
3. **Upload Evidence & SHA-256 Fingerprinting:**
   - On the Dashboard, locate the **Upload evidence** section.
   - Select an assigned case from the dropdown.
   - Choose `sample_evidence/synthetic_complaint_letter.pdf` (or drag & drop).
   - Click **Upload and calculate SHA-256**.
   - Show the immediate calculation of the 64-character SHA-256 hash.
   - Point out the **Copy hash** button for easy copying.
4. **Independent Hash Verification:**
   - In a terminal, run PowerShell:
     ```powershell
     Get-FileHash .\sample_evidence\synthetic_complaint_letter.pdf -Algorithm SHA256
     ```
   - Confirm that the terminal hash matches the platform's recorded hash character-for-character.
5. **Verify Evidence Integrity:**
   - Click **Verify integrity**.
   - Result: **MATCH (INTEGRITY VERIFIED)** in emerald green, showing recorded baseline and live hash.
6. **Controlled Tamper Detection Demonstration:**
   - Click **Run tamper test on a copy**.
   - Explain that an isolated copy is written to `app/test_copies/` and modified, while the original evidence in `app/uploads/` is preserved untouched.
   - The result panel shows:
     * **Tampered Copy:** **MISMATCH** (drastically different hash due to cryptographic avalanche effect).
     * **Original Evidence:** **MATCH** (remains pristine and bit-for-bit unchanged).
7. **Forensic Chain-of-Custody Audit Trail:**
   - Click **Audit Log** in the top navigation bar.
   - Demonstrate the complete immutable audit trail recording every upload, verification, and tamper test with officer name and timestamp.
8. **Word Documents & Extended File Support:**
   - Ingest modern Word documents (`.docx`) or legacy memos (`.doc`) with magic-byte validation and SHA-256 fingerprinting.
9. **Case Lifecycle (Closing & Re-opening with Audit Logging):**
   - In a Case Dossier, click **Close Case** to mark an investigation closed.
   - Click **Re-open Case** when supplemental evidence arises.
   - Every status transition is automatically audited as `CASE_CLOSED` or `CASE_REOPENED` with the acting investigator's badge in the Audit Log.
10. **Document Content Preview (Review 2 Sneak-Peek):**
   - Upload `sample_evidence/synthetic_chat_screenshot.png` or `synthetic_incident_note.txt`.
   - Inspect the evidence to show the inline image rendering and text preview.

---

## Automated Test Verification

Run all automated unit and route tests using pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**Result: 39 passed, 0 failed.**
- 10 Unit tests verifying SHA-256 calculation, NIST test vectors, and tamper detection isolation.
- 17 Integration tests verifying upload validation, magic bytes, path-traversal prevention, and verification states.
- 12 Feature tests verifying officer authentication, session protection, case management, DOC/DOCX ingestion, and audit logging.

---

## Review 1 Deliverables Summary

| Deliverable | Location |
|---|---|
| Project Overview, Problem Statement, Objectives, Scope & Limitations | [docs/project-overview.md](docs/project-overview.md) |
| System Architecture Specification & Component Diagram | [docs/system-architecture.md](docs/system-architecture.md) |
| Database ER Diagram & Relational Schema | [docs/database-design.md](docs/database-design.md) |
| Application Workflow Diagram & Pipeline | [docs/application-workflow.md](docs/application-workflow.md) |
| UI/UX Wireframes (Login, Dashboard, Evidence Ingestion, Analysis) | [docs/wireframes/README.md](docs/wireframes/README.md) |
| Team Responsibilities & Integration Plan (5-Member Breakdown) | [docs/team-responsibilities.md](docs/team-responsibilities.md) |
| 5-Day Review Preparation Timeline & Viva Q&A Guide | [docs/review-1-timeline.md](docs/review-1-timeline.md) |
| Working Prototype Codebase | `app/`, `run.py`, `config.py` |
| Automated Test Suite | `tests/`, `pytest` |
