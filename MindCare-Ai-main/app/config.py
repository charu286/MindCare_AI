# MindCare AI - Configuration
# Python is the single source of truth.

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mindcare-dev-secret-change-in-production")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "mindcare")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "mindcare")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "mindcare_ai")

    @staticmethod
    def mysql_dict():
        return {
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DATABASE,
        }

# Email (optional; contact form)
MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@mindcare.local")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")

JSON_DEFAULT_MEDICAL_DISCLAIMER = {"is_medical_advice": False}

DISCLAIMER_TEXT = (
    "MindCare AI is not a medical professional and does not replace therapy, "
    "diagnosis, or professional mental-health care."
)
