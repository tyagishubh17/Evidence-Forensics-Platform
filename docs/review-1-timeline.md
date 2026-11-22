# Review 1 Preparation Timeline (5 Days)

The "Status" column shows what exists in this repository. Items marked
**Team** need to be done by the team members themselves (for example,
presenting and rehearsing).

| Day | Tasks | Output | Status |
|---|---|---|---|
| **Day 1** | Finalise project proposal; problem statement; objectives; scope and limitations; technology stack | `project-overview.md`, `problem-statement.md`, `objectives-and-scope.md` | Drafted in repo, team review needed |
| **Day 2** | Architecture diagram; workflow diagram; database ER diagram; module responsibilities | `system-architecture.md`, `application-workflow.md`, `database-design.md`, `team-responsibilities.md`, `diagrams/` | Drafted in repo, team review needed |
| **Day 3** | UI wireframes; Flask project setup; file upload implementation; SHA-256 generation | `wireframes/`, `app/`, `config.py`, `run.py` | Done |
| **Day 4** | Integrity verification; prototype testing; documentation; presentation preparation | Verify and tamper-test routes, `tests/`, `README.md`, `prototype-test-report.md` | Code, tests and docs done. **Team:** prepare slides |
| **Day 5** | Final prototype demonstration; review presentation; technical question preparation | Live demo (see README), presentation, Q&A practice | **Team** |

## Day 5 checklist

- [ ] Every member can run the prototype from a fresh clone (README → *Setup*).
- [ ] `python -m pytest` passes on the demo laptop.
- [ ] Demo rehearsed once end to end (README → *Demonstration procedure*).
- [ ] Slides include the architecture, ER, workflow and wireframe images from `docs/`.
- [ ] Each member can explain their proposed responsibility and next steps.
- [ ] Database is reset before the review (delete `instance/evidence.db` and
      the files in `app/uploads/` and `app/test_copies/`, keeping `.gitkeep`).

## Likely technical questions (preparation)

| Question | Short answer |
|---|---|
| Why SHA-256 and not MD5 / SHA-1? | Practical collision attacks exist for MD5 and SHA-1. SHA-256 (FIPS 180-4) has no known practical collisions and is widely used for evidence integrity. |
| What does a MATCH actually prove? | That the stored file is bit-for-bit identical to what was uploaded. It does not prove the file was genuine before upload. |
| Why is the file saved under a random name? | So a user-supplied name like `../../x` cannot write outside the upload folder (path traversal), and so two files with the same name do not overwrite each other. |
| How do you know the original is not modified by the tamper test? | The test copies the file into a separate `test_copies/` folder and modifies only the copy. The original is re-verified (MATCH) and an automated test checks it byte for byte. |
| Why hash in chunks? | So large files do not need to be loaded fully into memory. The result is identical to hashing the whole file at once, and a test confirms this. |
| Could someone change both the file and the stored hash? | In this prototype, yes, if they had server access. Later mitigations include access control, an append-only activity log, and exporting hashes in the signed PDF report. |
| Why SQLite? | It needs no server, is built into Python and suits a small team and data volume. Migrating to PostgreSQL later would be straightforward. |
| Why not build everything now? | Review 1 focuses on a reliable foundation. Modules 2–4 are planned for later reviews (see `objectives-and-scope.md`). |
