# MindCare AI - Configuration
# Python is the single source of truth.

import os
from pathlib import Path

# Base
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mindcare-dev-secret-change-in-production")
    # MySQL
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "mindcare")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "mindcare")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "mindcare_ai")
    # SQLAlchemy-style URI for mysql-connector
    @staticmethod
    def mysql_uri():
        c = Config
        return {
            "host": c.MYSQL_HOST,
            "port": c.MYSQL_PORT,
            "user": c.MYSQL_USER,
            "password": c.MYSQL_PASSWORD,
            "database": c.MYSQL_DATABASE,
        }

# Non-negotiable: every JSON response must include this
JSON_DEFAULT_MEDICAL_DISCLAIMER = {"is_medical_advice": False}

DISCLAIMER_TEXT = (
    "MindCare AI is not a medical professional and does not replace therapy, "
    "diagnosis, or professional mental-health care."
)
