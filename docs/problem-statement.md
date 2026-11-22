# Problem Statement

## Statement

Investigators at the station and cyber-cell level often receive digital
evidence (PDF documents, screenshots, scanned images and text files) through
many channels. These files are commonly stored in personal folders, e-mail or
messaging applications without a consistent structure. **There is often no
simple, centralised way to:**

1. keep evidence files organised by investigation case,
2. record a reliable fingerprint of each file when it is received, and later
   check that the file has not been changed, and
3. extract and summarise the useful information inside these files for a
   preliminary report.

As a result, evidence can be hard to locate, its integrity can be difficult to
demonstrate later, and investigators spend considerable time manually reading
documents and preparing reports.

## Who is affected

- Police personnel and cybercrime investigation teams handling digital complaints.
- Supervisors who need a clear overview of the evidence collected for a case.

## Why it matters

- **Integrity.** If a file changes after collection, even accidentally, its
  reliability can be questioned. Without a recorded hash, such changes may not
  be noticed.
- **Efficiency.** Manual reading and note-taking is slow and repetitive,
  particularly when a case involves many documents.
- **Consistency.** Without a standard workflow, different investigators record
  file details and findings in different ways.

## What this project will address

The project will build a basic web platform that:

- organises evidence by case,
- generates and stores a SHA-256 hash for each uploaded file and verifies it on demand,
- extracts text and simple entities from documents and images as a
  *preliminary* aid, and
- generates a structured PDF report for investigator review.

## What this project will not claim

- It does **not** guarantee legal admissibility of any evidence.
- It does **not** identify suspects or criminals automatically.
- It does **not** replace trained forensic examiners or certified forensic tools.
- A matching hash shows that a file is unchanged **since it was uploaded to this
  system**. It cannot prove that the file was authentic before upload.
