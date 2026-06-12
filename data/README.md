# Data Directory

Local working directory for files used during development and experimentation.

- `resumes/` — raw resume files (PDF/DOCX/TXT) used for local testing.
- `job_descriptions/` — raw job description files used for local testing.
- `processed/` — intermediate/processed outputs (e.g. parsed text, extracted features).

This directory is intended for local development data only. Actual file
contents are excluded from version control via `.gitignore` to avoid
committing potentially sensitive personal data (PII) — only the folder
structure (via `.gitkeep` files) is tracked.
