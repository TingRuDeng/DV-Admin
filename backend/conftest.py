import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_admin.settings_test")
