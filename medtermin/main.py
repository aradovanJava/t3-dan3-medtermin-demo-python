"""Aplikacija za uvicorn: ``uvicorn medtermin.main:app --reload --port 8000``."""

from medtermin.app import create_app
from medtermin.logiranje import nastavi_logiranje

nastavi_logiranje()
app = create_app()
