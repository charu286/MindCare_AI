# MindCare AI - MySQL connection and helpers
# Uses mysql-connector-python.

import uuid
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from app.config import Config

def get_conn():
    return mysql.connector.connect(**Config.mysql_dict())

@contextmanager
def db_cursor(dictionary=True):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()

def get_or_create_user_uuid(cursor, user_uuid=None):
    if user_uuid:
        cursor.execute("SELECT id FROM users WHERE user_uuid = %s", (user_uuid,))
        row = cursor.fetchone()
        if row:
            return row["id"], str(user_uuid)
    u = str(uuid.uuid4())
    # is_anonymous defaults to TRUE when column exists; anon INSERT avoids auth columns
    try:
        cursor.execute("INSERT INTO users (user_uuid, is_anonymous) VALUES (%s, TRUE)", (u,))
    except Exception:
        cursor.execute("INSERT INTO users (user_uuid) VALUES (%s)", (u,))
    return cursor.lastrowid, u


def get_user_by_email(cursor, email):
    cursor.execute(
        "SELECT id, user_uuid, email, is_anonymous FROM users WHERE email = %s", (email,)
    )
    return cursor.fetchone()


def get_user_by_uuid(cursor, user_uuid):
    if not user_uuid:
        return None
    cursor.execute(
        "SELECT id, user_uuid, email, is_anonymous FROM users WHERE user_uuid = %s",
        (user_uuid,),
    )
    return cursor.fetchone()


def create_registered_user(cursor, email, password_hash):
    u = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (user_uuid, email, password_hash, is_anonymous) VALUES (%s, %s, %s, FALSE)",
        (u, email, password_hash),
    )
    return cursor.lastrowid, u


def update_user_to_registered(cursor, user_uuid, email, password_hash):
    cursor.execute(
        "UPDATE users SET email = %s, password_hash = %s, is_anonymous = FALSE WHERE user_uuid = %s",
        (email, password_hash, user_uuid),
    )


def migrate_anon_to_user(cursor, from_user_id, to_user_id):
    """Move sessions, daily_trends, assessment_results from anon user to registered user."""
    cursor.execute("UPDATE sessions SET user_id = %s WHERE user_id = %s", (to_user_id, from_user_id))
    cursor.execute("UPDATE daily_trends SET user_id = %s WHERE user_id = %s", (to_user_id, from_user_id))
    cursor.execute("UPDATE assessment_results SET user_id = %s WHERE user_id = %s", (to_user_id, from_user_id))

def get_or_create_session(cursor, user_id):
    # Reuse open session for multi-turn chat; create only if none.
    cursor.execute(
        "SELECT id, session_uuid FROM sessions WHERE user_id = %s AND ended_at IS NULL ORDER BY started_at DESC LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"], row["session_uuid"]
    s = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO sessions (user_id, session_uuid) VALUES (%s, %s)",
        (user_id, s),
    )
    return cursor.lastrowid, s


def get_recent_messages(cursor, session_id, limit=10):
    cursor.execute(
        "SELECT role, content FROM conversation_history WHERE session_id = %s ORDER BY id DESC LIMIT %s",
        (session_id, limit),
    )
    rows = cursor.fetchall() or []
    return [{"role": r["role"], "content": (r["content"] or "")[:500]} for r in reversed(rows)]

def log_message(cursor, session_id, role, content, meta=None):
    import json
    cursor.execute(
        """INSERT INTO conversation_history (session_id, role, content, meta)
           VALUES (%s, %s, %s, %s)""",
        (session_id, role, content, json.dumps(meta) if meta else None),
    )

def upsert_daily_trend(cursor, user_id, date, avg_stress, peak_stress):
    cursor.execute(
        """INSERT INTO daily_trends (user_id, date, avg_stress, peak_stress, session_count)
           VALUES (%s, %s, %s, %s, 1)
           ON DUPLICATE KEY UPDATE
             avg_stress = (avg_stress * session_count + %s) / (session_count + 1),
             peak_stress = GREATEST(peak_stress, %s),
             session_count = session_count + 1""",
        (user_id, date, avg_stress, peak_stress, avg_stress, peak_stress),
    )


def save_contact_submission(cursor, topic, email, message):
    cursor.execute(
        """INSERT INTO contact_submissions (topic, email, message) VALUES (%s, %s, %s)""",
        (topic, email, message),
    )
    return cursor.lastrowid


def fetch_fears_phobias(cursor):
    cursor.execute(
        """SELECT name, meaning, description, emoji_or_icon FROM fears_phobias ORDER BY sort_order, name"""
    )
    return cursor.fetchall() or []


def save_assessment_result(cursor, user_id, assessment_type, total_score, severity, answers_json=None):
    cursor.execute(
        """INSERT INTO assessment_results (user_id, assessment_type, total_score, severity, answers_json)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, assessment_type, total_score, severity, answers_json),
    )
    return cursor.lastrowid
