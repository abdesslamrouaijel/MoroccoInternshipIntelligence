from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EXPORT_DIR = DATA_DIR / "exports"
DATABASE_URL = os.getenv("MII_DATABASE_URL", f"sqlite:///{(DATA_DIR / 'morocco_internships.db').as_posix()}")
SEARCH_TERMS = [
    "stage PFE 2027 Maroc ingénieur",
    "stage fin d'études Maroc informatique",
    "stage PFE data science Maroc",
    "stage ingénieur robotique IoT Maroc",
    "stage maintenance industrielle Maroc",
    "final year internship Morocco engineering",
]
REGIONS = [
    "Casablanca-Settat", "Rabat-Salé-Kénitra", "Tanger-Tétouan-Al Hoceïma",
    "Fès-Meknès", "Marrakech-Safi", "Souss-Massa", "Oriental",
    "Béni Mellal-Khénifra", "Drâa-Tafilalet", "Guelmim-Oued Noun",
    "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab",
]
