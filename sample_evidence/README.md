# Synthetic sample files

All files in this folder are **synthetic** and were generated for testing.
They contain no real records, people or evidence.

| File | Purpose | Expected result | SHA-256 |
|---|---|---|---|
| `synthetic_incident_note.txt` | Valid plain-text note | Accepted | `fac90f0ef585c50d727ac44b9c4118ea377cd114472019103ac400fd30388ae6` |
| `synthetic_complaint_letter.pdf` | Valid one-page PDF | Accepted | `62558c80184d10260684c015be9bbc69cf3f8b2a13ea7d7a07d34aabebfec23c` |
| `synthetic_chat_screenshot.png` | Valid PNG placeholder image | Accepted | `1aae81bd8a0574057d7ba84cf9b4ea52f2e56f50e93c08a38b081f36f9f70868` |
| `not_really_a_pdf.pdf` | Text file renamed to `.pdf` | Rejected: content does not match the extension | n/a |
| `invalid_type_example.bak` | Disallowed file type | Rejected: not an allowed file type | n/a |

The hashes can be checked independently, which is a good step to show in the demo:

- Windows (PowerShell): `Get-FileHash .\synthetic_complaint_letter.pdf -Algorithm SHA256`
- Windows (cmd): `certutil -hashfile synthetic_complaint_letter.pdf SHA256`
- macOS / Linux: `shasum -a 256 synthetic_complaint_letter.pdf`

PowerShell prints the hash in upper case, and the application shows it in
lower case. The value is the same.
