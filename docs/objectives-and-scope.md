# Objectives, Scope and Limitations

## 1. Project objectives

1. **Centralised evidence organisation.** Develop a web application in which
   authorised investigators can create investigation cases and upload digital
   evidence files (PDF, JPG/JPEG, PNG, TXT) to them.
2. **Evidence integrity.** Generate a SHA-256 hash for every uploaded file at
   the time of upload, store it with the file's metadata, and allow the
   investigator to re-verify the file at any time (MATCH / MISMATCH).
3. **Information extraction.** Extract text from PDF documents and images (OCR)
   and identify basic entities such as names, phone numbers, e-mail addresses
   and dates as a preliminary aid for the investigator.
4. **Organisation and timeline.** Present evidence and extracted information per
   case, including a simple chronological timeline of evidence and dates found
   in the documents.
5. **Structured reporting.** Generate a downloadable PDF report that summarises
   the case, its evidence files, their hashes and the preliminary findings, for
   review by the investigator.

## 2. Finalised functional scope (complete project)

| Module | Functions | Planned review |
|---|---|---|
| **1. Evidence Management and Integrity** | Case creation and management · evidence file upload · file metadata recording · SHA-256 hash generation · integrity verification · basic activity logging | Review 1 (prototype), Review 2 (complete) |
| **2. Preliminary AI-Assisted Analysis** | PDF text extraction (PyMuPDF) · image OCR (Tesseract) · basic entity extraction (spaCy + regular expressions) · document summarisation (optional Gemini API) | Review 2 |
| **3. Evidence Organisation and Timeline** | Organising evidence by case · displaying extracted information · chronological evidence timeline | Review 2 / 3 |
| **4. Dashboard and Report Generation** | Case dashboard · evidence analysis display · downloadable PDF reports (ReportLab) | Review 3 |

*The review allocation for Modules 2–4 is a proposed plan and may be adjusted
with the supervisor.*

## 3. Review 1 scope (what is built now)

A small working prototype of part of Module 1:

**File upload → SHA-256 hash generation → file information display → integrity verification**

- Upload of PDF, JPG, JPEG, PNG and TXT files with validation (type, empty
  file, size limit, content signature).
- SHA-256 hash generated with Python `hashlib` immediately after upload and
  stored with the file's metadata in SQLite.
- File information display: name, type, MIME type, size, upload time and full hash.
- Integrity verification of the stored original (MATCH / MISMATCH / file missing).
- A controlled tamper-detection demonstration that modifies a **copy** in a
  separate folder and shows a MISMATCH, while the original still shows MATCH.

**Explicitly not built in Review 1:** login, case management, AI analysis,
OCR, entity extraction, timeline, dashboard, PDF reports.

## 4. Overall project scope

**In scope:**
- A single web application for use on a local machine or an internal network.
- The file types PDF, JPG/JPEG, PNG and TXT.
- English-language text extraction and entity recognition.
- Preliminary, assistive analysis that the investigator reviews.
- Synthetic test data only.

**Out of scope:**
- Disk imaging, mobile phone extraction, memory forensics or recovery of deleted data.
- Call detail record (CDR) analysis, criminal network detection or cross-case analysis.
- Automatic identification of suspects or determination of guilt.
- Integration with official police databases or case-management systems.
- Production deployment, high availability or large-scale storage.

## 5. Limitations

1. **Academic prototype.** The application is not certified, audited or
   validated against forensic standards and must not be used for real cases.
2. **Integrity starts at upload.** The hash proves a file is unchanged *since it
   was uploaded*, not that it was genuine or unaltered before upload.
3. **No legal guarantee.** The project does not guarantee that evidence handled
   with it is legally admissible.
4. **AI and OCR accuracy.** OCR, entity extraction and summarisation (planned)
   can be wrong or incomplete, especially for poor-quality images, handwriting
   or non-English text. All results must be checked by a person.
5. **Security.** Basic secure-coding practices are followed (allowed file
   types, safe file names, environment variables for secrets), but the system
   has not had a professional security assessment. Files are not encrypted at
   rest.
6. **Scale.** SQLite and local file storage suit a small team and modest data
   volumes, not large deployments.
7. **External AI service.** If the optional Gemini API is used, document text
   would be sent to an external service. This is unsuitable for real
   confidential material and is limited to synthetic data in this project.
8. **Time and team size.** With 4–5 members over 2–3 months, features are
   intentionally kept basic.
