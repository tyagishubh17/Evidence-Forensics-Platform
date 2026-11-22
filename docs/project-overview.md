# Project Overview

**Project title:** AI-Driven Digital Evidence Management and Preliminary Analysis Platform
**Course:** Engineering Projects in Community Service (EPICS)
**Domain:** Digital forensics, evidence management and artificial intelligence
**Current milestone:** Review 1: project foundation and initial prototype

> This is an academic EPICS project. It is a learning-oriented prototype, not a
> certified or production-grade forensic product.

---

## 1. Overview

Investigators increasingly receive evidence as digital files: complaint letters
as PDFs, screenshots of chats, scanned documents and plain-text notes. This
project proposes a web-based platform where an investigator can:

- keep these files together under an investigation case,
- record a cryptographic fingerprint (SHA-256 hash) of each file at the moment it
  is received, so later changes can be detected,
- extract text and basic information (names, phone numbers, dates, etc.) from
  documents and images, and
- produce a structured preliminary report that a human investigator reviews.

The platform is intended to make the **initial handling and organisation** of
digital evidence simpler and more consistent. Analysis results are aids for the
investigator, not conclusions.

## 2. Background and motivation

- **Volume and variety of digital material.** Even minor cyber-related
  complaints can involve many screenshots, documents and exported messages.
  When these are kept in personal folders, e-mail attachments or messaging
  apps, they are hard to locate, compare and report on.
- **Integrity is easy to lose and hard to show later.** A file that is renamed,
  re-saved or compressed may no longer be byte-for-byte identical to what was
  received. Cryptographic hash values are the standard way to show that a digital
  file has not changed. For example, in India the certificate format under
  Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 asks for the hash value of
  an electronic record. *(The team should confirm current legal requirements with
  the supervisor. This project does not provide legal certification.)*
- **Manual reading takes time.** Reading every document to note names, numbers
  and dates is repetitive. Text extraction and simple entity extraction can
  reduce this effort, as long as the investigator still checks the output.
- **Community relevance.** Police stations and cyber cells, especially smaller
  units, may not have access to commercial forensic suites. A simple, free and
  well-documented tool for organising evidence and checking integrity is a
  meaningful community-service contribution and a good learning project.

## 3. Proposed solution

A Flask web application, organised into four modules:

| Module | Purpose | Review 1 status |
|---|---|---|
| 1. Evidence Management and Integrity | Cases, uploads, metadata, SHA-256 hashing, integrity verification, activity log | **Prototype of upload, metadata, SHA-256 and verification implemented** |
| 2. Preliminary AI-Assisted Analysis | PDF text extraction, image OCR, entity extraction, summarisation | Planned |
| 3. Evidence Organisation and Timeline | Evidence grouped by case, extracted information display, chronological timeline | Planned |
| 4. Dashboard and Report Generation | Case dashboard, analysis display, downloadable PDF reports | Planned |

Technology: HTML/CSS/Bootstrap/JavaScript frontend, Python Flask backend, SQLite
database, Python `hashlib` for SHA-256, and (planned) PyMuPDF, Tesseract OCR,
spaCy, regular expressions, ReportLab and an optional Gemini API integration.
See [system-architecture.md](system-architecture.md).

## 4. Target beneficiaries

- **Police personnel** at station level who receive digital complaints and
  attachments.
- **Cybercrime investigation teams** that need an organised, integrity-checked
  record of collected files.
- **Other authorised investigators** (for example, internal inquiry teams in
  institutions) handling digital documents.
- **Students and trainers** who can use the project to learn basic digital
  evidence handling concepts.

The platform is intended for authorised users only. The Review 1 prototype is
tested exclusively with synthetic sample files.

## 5. Expected outcomes

By the end of the project (all three reviews), the team expects to deliver:

1. A working web application in which an investigator can create a case, upload
   evidence and see each file's recorded SHA-256 hash.
2. On-demand integrity verification that clearly reports MATCH or MISMATCH.
3. Text extraction from PDFs and images, with basic entities highlighted for
   investigator review.
4. A per-case view and a simple chronological timeline of evidence.
5. A downloadable PDF report summarising the case, its evidence, hashes and
   preliminary findings.
6. Documentation, test cases and a demonstration using synthetic data only.

**Outcome at Review 1:** project documentation, design diagrams, wireframes and
a working, tested prototype of upload → SHA-256 → metadata display → integrity
verification, including a tamper-detection demonstration.

## 6. Proposed future enhancements

These are ideas beyond the planned scope, listed for completeness. None are
implemented.

- Role-based access (for example, investigator, supervisor and read-only reviewer).
- A full chain-of-custody log recording who accessed or exported each file, and when.
- Support for more file types (DOCX, audio and video metadata).
- Multilingual OCR (for example, Hindi and other regional languages through Tesseract language packs).
- Searching across all extracted text within a case.
- Optional encryption of stored evidence files at rest.
- Deployment on an institution's internal server with HTTPS.
- Cross-case analysis and link analysis (only after careful review of privacy
  and accuracy concerns).

## Related documents

- [Problem statement](problem-statement.md)
- [Objectives, scope and limitations](objectives-and-scope.md)
- [System architecture](system-architecture.md)
- [Database design](database-design.md)
- [Application workflow](application-workflow.md)
- [UI wireframes](wireframes/README.md)
- [Team responsibilities](team-responsibilities.md)
- [Review 1 timeline](review-1-timeline.md)
- [Prototype test report](prototype-test-report.md)
