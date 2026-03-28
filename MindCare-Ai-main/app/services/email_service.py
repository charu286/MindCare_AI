# MindCare AI - Email (smtplib). Graceful if not configured.

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config


def send_contact_notification(topic: str, email: str, message: str):
    """Returns (success, error_message)."""
    if not Config.MAIL_SERVER or not Config.ADMIN_EMAIL:
        return False, "Email not configured"
    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"[MindCare Contact] {topic}"
        msg["From"] = Config.MAIL_DEFAULT_SENDER
        msg["To"] = Config.ADMIN_EMAIL
        body = f"Topic: {topic}\nFrom: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as s:
            if Config.MAIL_USE_TLS:
                s.starttls()
            if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                s.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            s.send_message(msg)
        return True, ""
    except Exception as e:
        return False, str(e)
