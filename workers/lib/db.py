"""DB access for worker jobs — reuses the backend's engine and models.

Run jobs from the repo root with the backend's venv:
    backend/.venv/Scripts/python.exe -m workers.jobs.refresh_hpi
"""

from app.db import SessionLocal

__all__ = ["SessionLocal"]
