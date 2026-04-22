import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = ROOT_DIR / "StayEase"

# Ensure Django project package is importable on Vercel.
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stayease.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
