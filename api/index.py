"""Vercel entry point for the FastAPI application.

The frontend and API are deployed together.  Keeping this thin wrapper at the
repository root lets Vercel discover it while the Python application remains
organised in ``backend/app`` for local development and tests.
"""

from pathlib import Path
import sys


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.main import app  # noqa: E402
