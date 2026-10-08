from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "generated_reports"
FRONTEND_DIR = ROOT / "frontend"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SCORING_WEIGHTS = {
    "spatial": 0.35,
    "waste": 0.30,
    "capacity": 0.20,
    "temporal": 0.10,
    "regulatory": 0.05,
}
