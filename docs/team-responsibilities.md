# Team Responsibilities (Proposed)

> This is a **proposed** division of work for the project. It does not indicate
> that any member has completed these tasks. Replace "Member 1–5" with names.

## Five-member team

| Member | Role | Main responsibilities | Modules | Review 1 contribution (proposed) |
|---|---|---|---|---|
| Member 1 | Frontend development and UI design | Wireframes, page templates (HTML/Jinja), Bootstrap layout, CSS theme, client-side checks, usability | All UI; Module 3 & 4 screens | Wireframes, upload and verification page styling |
| Member 2 | Flask backend and application logic | Routes, request handling, validation, error handling, later authentication and case management | Module 1 (backend), integration point for 2–4 | Upload, verify and tamper-test routes |
| Member 3 | Database design, file storage and evidence integrity | ER design, SQLite schema, storage folders, SHA-256 hashing and verification, activity log | Module 1 (data & integrity) | ER diagram, evidence table, `integrity.py` |
| Member 4 | Document processing and AI research | Research and prototype PyMuPDF, Tesseract OCR, spaCy, regex patterns, optional Gemini summarisation | Module 2, input to Module 3 | Technology research notes, test documents for Review 2 |
| Member 5 | Integration, reporting, documentation and testing | Git workflow, merging modules, ReportLab report, pytest tests, documentation, demo preparation | Module 4, cross-module testing | Tests, README, documentation, presentation |

## Four-member team

As suggested in the plan, the database and integration roles are combined:

| Member | Role |
|---|---|
| Member 1 | Frontend development and UI design |
| Member 2 | Flask backend and application logic |
| Member 3 | **Database, file storage, evidence integrity + integration and testing** |
| Member 4 | Document processing, AI research **+ report generation and documentation** |

Documentation and testing should be shared, with every member writing tests and
notes for their own code.

## How the modules will be integrated

1. **One repository, one Flask application.** All modules live in the same Git
   repository and the same `app/` package. There are no separate services.
2. **Agreed interfaces first.** Plain Python functions with simple inputs and
   outputs form the contract between members. For example:
   - `calculate_sha256(path) -> str` and `verify_integrity(path, recorded_hash) -> dict` (Module 1, done)
   - planned: `extract_text(path) -> str`, `extract_entities(text) -> dict`, `summarise(text) -> str` (Module 2)
   - planned: `build_case_report(case_id) -> bytes` (Module 4)

   Routes (Member 2) call these functions. The processing code (Member 4) does not
   need to know about Flask.
3. **Shared database schema.** Member 3 owns the schema. Other modules read and
   write through small helper functions in `app/db.py`, so table changes happen
   in one place.
4. **Branches and pull requests.** Each feature is built on its own branch
   (`feature/upload`, `feature/ocr`, …) and merged into `main` through a pull
   request that another member reviews. `main` should always run.
5. **Tests before merge.** Each module adds pytest tests under `tests/`. The
   integration lead runs the full suite before merging.
6. **Synthetic data only.** Every member uses the files in `sample_evidence/` or
   other synthetic files. No real records are committed or shared.
7. **Integration checkpoints.** A short end-to-end check before each review:
   upload → hash → (extract → analyse) → display → report.
