# MindCare AI - Auth: optional Login/Register, session-based. Non-forceful, ethical.

import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.auth_utils import hash_password, check_password
from app.database import (
    db_cursor,
    get_user_by_email,
    get_user_by_uuid,
    create_registered_user,
    update_user_to_registered,
    migrate_anon_to_user,
)

auth_bp = Blueprint("auth", __name__)


def _valid_email(s):
    return bool(s and re.match(r"^[^@]+@[^@]+\.[^@]+$", s) and len(s) <= 255)


def _valid_password(s):
    return bool(s and len(s) >= 6 and len(s) <= 200)


@auth_bp.route("/")
def auth_page():
    return render_template("auth.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    j = request.get_json(silent=True) or {}
    email = (request.form.get("email") or j.get("email")) or ""
    email = email.strip().lower()
    password = (request.form.get("password") or j.get("password")) or ""

    if not _valid_email(email):
        flash("Please enter a valid email.", "error")
        return redirect(url_for("auth.auth_page"))
    if not _valid_password(password):
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("auth.auth_page"))

    try:
        with db_cursor() as cur:
            existing = get_user_by_email(cur, email)
            if existing:
                flash("An account with this email already exists. Try logging in.", "error")
                return redirect(url_for("auth.auth_page"))

            anon_uuid = session.get("user_uuid")
            anon_user = get_user_by_uuid(cur, anon_uuid) if anon_uuid else None

            if anon_user and (anon_user.get("is_anonymous") in (True, 1)):
                # Upgrade: keep anon data, just set email/password on same row
                update_user_to_registered(cur, str(anon_uuid), email, hash_password(password))
                session["is_registered"] = True
                # user_uuid unchanged; already in session
            else:
                # New user
                uid, u = create_registered_user(cur, email, hash_password(password))
                session["user_uuid"] = u
                session["is_registered"] = True

        flash("Account created. You can now use Dashboard and save your progress.", "success")
        return redirect(url_for("page.dashboard"))
    except Exception:
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.auth_page"))


@auth_bp.route("/login", methods=["POST"])
def login():
    j = request.get_json(silent=True) or {}
    email = (request.form.get("email") or j.get("email")) or ""
    email = email.strip().lower()
    password = (request.form.get("password") or j.get("password")) or ""

    if not _valid_email(email) or not password:
        flash("Please enter your email and password.", "error")
        return redirect(url_for("auth.auth_page"))

    try:
        with db_cursor() as cur:
            user = get_user_by_email(cur, email)
            if not user or not check_password(password, user.get("password_hash") or ""):
                flash("Email or password is incorrect.", "error")
                return redirect(url_for("auth.auth_page"))

            to_id = user["id"]
            to_uuid = user["user_uuid"]

            # If current session has an anon user, migrate their data to this account
            anon_uuid = session.get("user_uuid")
            anon_user = get_user_by_uuid(cur, anon_uuid) if anon_uuid else None
            if anon_user and anon_user.get("id") != to_id and (anon_user.get("is_anonymous") in (True, 1)):
                migrate_anon_to_user(cur, anon_user["id"], to_id)

            session["user_uuid"] = to_uuid
            session["is_registered"] = True

        flash("You’re logged in. Your progress is now saved to your account.", "success")
        return redirect(url_for("page.dashboard"))
    except Exception:
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.auth_page"))


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_uuid", None)
    session.pop("is_registered", None)
    return redirect(url_for("page.home"))
