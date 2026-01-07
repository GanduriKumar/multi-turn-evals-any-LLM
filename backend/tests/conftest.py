import sys
from pathlib import Path

# Ensure the backend folder is on sys.path so tests can import modules like
# `from metrics import ...` which live under backend/metrics.py
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
