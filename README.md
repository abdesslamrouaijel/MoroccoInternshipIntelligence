# Morocco Internship Intelligence

A Windows desktop application for discovering public internship-market listings, recording company leads, analyzing offer text, tracking applications, and exporting reports. Python 3.11+ is required; tested with Python 3.12.

## Install and launch

1. Install Python 3.11 or newer and ensure `python` is on PATH.
2. From this folder, create an isolated environment: `python -m venv .venv`.
3. Install dependencies: `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Optional: copy `.env.example` to `.env` and configure `MII_DATABASE_URL` in the process environment. The default SQLite file is created at `data/morocco_internships.db`.
5. Initialize the database with `.venv\Scripts\python.exe -m database.init_db`.
6. Launch with `run.bat` or `.venv\Scripts\python.exe main.py`.
7. Run tests with `.venv\Scripts\python.exe -m pytest`.

## Features

- **Dashboard:** saved-offer and company counts, recent opportunities, and new-link count.
- **Internship Market Search:** searches public DuckDuckGo HTML results and stores discovered links. Search terms can be edited; results are not represented as verified job announcements.
- **LinkedIn:** opens a LinkedIn job search in the user's browser and supports manual import of public URLs and copied announcement text. The application does not sign in, scrape authenticated pages, automate accounts, or bypass CAPTCHA/access controls.
- **Companies by Region:** returns public search-result leads for a Moroccan region/city. The user selects a result to save it as an explicitly unverified lead. Company size, contact information, and employment claims are never invented.
- **Recruitment Analysis:** heuristic PFE/engineering detection, skill extraction, and a 0–100 relevance indicator. It is not a hiring probability. Configure skills and academic background in Settings.
- **Saved Opportunities:** filter offers, track status, and save private notes. Double-click a title to open its announcement when a URL is displayed in that row.
- **Reports & Exports:** CSV, JSON, XLSX, and PDF exports are written to `data/exports/`.

## Search and data limitations

The public-web integration uses DuckDuckGo's HTML search endpoint through ordinary HTTP requests. It is subject to connectivity, provider layout/rate limits, and terms of service; failures are reported in the UI and never shown as successful empty searches. Search snippets and company leads are unverified and should be checked at the source. Publication dates, application deadlines, recruiter contacts, industry, and company size are not reliably extracted by this initial version. LinkedIn requires manual browser access/import. There is no paid API integration or automated scheduled monitoring.

Data is stored locally in SQLite. Avoid sharing the database if it contains private application notes. No credentials or API keys are required for the implemented search.

## Build a Windows executable

Install dependencies, then run `build_exe.bat`. PyInstaller writes build artifacts to `build/` and `dist/`. Run the resulting executable on Windows to validate its dependencies and data-directory permissions.
