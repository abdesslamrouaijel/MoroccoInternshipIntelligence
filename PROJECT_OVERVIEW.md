# Morocco Internship Intelligence: repository guide

A Windows-oriented Python desktop application for finding public internship-market leads, organizing opportunities and companies, and exporting reports. See `README.md` for installation, usage, and important data limitations.

## Project map

- `main.py` — starts the desktop interface.
- `frontend/` — application window and interface.
- `backend/` — public search, text analysis, deduplication, and export functions.
- `services/` — application operations for stored data and related workflows.
- `database/` — database models, connection, and initialization.
- `config/` and `.env.example` — configuration and example environment settings.
- `tests/` — automated tests.
- `requirements.txt`, `run.bat`, and `build_exe.bat` — dependencies, launch, and Windows build entry points.

Search results and company leads are unverified; the existing README explains provider and data limitations. The existing project structure and source files are preserved.
