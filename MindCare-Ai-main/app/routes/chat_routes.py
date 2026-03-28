# MindCare AI - Chat: multi-turn, context-aware, empathy-first. Safety always on.

from flask import Blueprint, render_template, request, jsonify, session
from app.database import (
    db_cursor, get_or_create_user_uuid, get_or_create_session, get_recent_messages,
    log_message, upsert_daily_trend,
)
from app.services import compute_risk, analyze_emotion, check_crisis, generate_advice
from datetime import date

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/")
def chat_page():
    return render_template("chat.html")

@chat_bp.route("/history", methods=["GET"])
def chat_history():
    """Return recent messages for the current session for multi-turn continuity."""
    out = []
    try:
        with db_cursor() as cur:
            uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
            session["user_uuid"] = _
            sid, _ = get_or_create_session(cur, uid)
            out = get_recent_messages(cur, sid, limit=20)
    except Exception:
        pass
    return _json_response({"messages": out})

def _json_response(data):
    out = dict(data)
    out["is_medical_advice"] = False
    return jsonify(out)

@chat_bp.route("/message", methods=["POST"])
def chat_message():
    """
    Each message uses predict logic plus conversation context. Returns empathetic reply.
    Multi-turn: reuses session, fetches recent messages, passes to advice for continuity.
    Safety: check_crisis always runs; crisis overrides normal advice.
    """
    text = None
    if request.is_json:
        text = (request.get_json() or {}).get("text") or ""
    else:
        text = (request.form or {}).get("text") or ""
    text = (text or "").strip()

    uid, sid, recent = None, None, []
    try:
        with db_cursor() as cur:
            uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
            session["user_uuid"] = _
            sid, _ = get_or_create_session(cur, uid)
            recent = get_recent_messages(cur, sid, limit=10)
    except Exception:
        pass

    risk_out = compute_risk(text)
    risk_score = risk_out["risk_score"]
    emotion_out = analyze_emotion(text, risk_score)
    crisis_out = check_crisis(text)
    advice_out = generate_advice(
        text,
        emotion_out["tone"],
        emotion_out["emotion_category"],
        crisis_out.get("is_crisis", False),
        crisis_out if crisis_out.get("is_crisis") else None,
        recent_messages=recent,
    )

    reply = advice_out.get("advice", "")
    steps = advice_out.get("steps", [])
    if steps:
        reply += "\n\n" + "\n".join("• " + s for s in steps)
    h = advice_out.get("helpline_guidance", [])
    if h:
        reply += "\n\nHelplines:\n" + "\n".join("• " + x for x in h)

    try:
        with db_cursor() as cur:
            if uid is None or sid is None:
                uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
                session["user_uuid"] = _
                sid, _ = get_or_create_session(cur, uid)
            meta = {"risk_score": risk_score, "emotion_category": emotion_out["emotion_category"], "tone": emotion_out["tone"], "is_crisis": crisis_out.get("is_crisis", False)}
            log_message(cur, sid, "user", text, meta)
            log_message(cur, sid, "assistant", reply, None)
            upsert_daily_trend(cur, uid, date.today().isoformat(), risk_score * 100, risk_score * 100)
    except Exception:
        pass

    return _json_response({
        "reply": reply,
        "is_crisis": advice_out.get("is_crisis", False),
        "is_medical_advice": False,
    })
