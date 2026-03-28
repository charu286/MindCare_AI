# MindCare AI - API v1 (e.g. /api/v1/predict)
# Every JSON response includes is_medical_advice: false.

import json
import re
from datetime import date
from flask import Blueprint, request, jsonify, session
from app.config import Config
from app.database import (
    db_cursor, get_or_create_user_uuid, get_or_create_session, log_message, upsert_daily_trend,
    save_contact_submission, save_assessment_result,
)
from app.services import compute_risk, analyze_emotion, check_crisis, generate_advice
from app.services.email_service import send_contact_notification
from app.services.mcq_service import get_mcq, score_mcq

api_bp = Blueprint("api", __name__)

def _json_response(data):
    out = dict(data)
    out["is_medical_advice"] = False
    return jsonify(out)

@api_bp.route("/predict", methods=["POST"])
def predict():
    """
    Text analysis. Expects JSON: { "text": "..." } or form "text".
    Returns: risk_score (0-100%), emotion_category, tone, confidence, keyword_counts,
             advice, steps, is_crisis, helpline_guidance (if crisis).
    """
    text = None
    if request.is_json:
        text = (request.get_json() or {}).get("text") or ""
    else:
        text = (request.form or {}).get("text") or ""
    text = (text or "").strip()

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
    )

    # Persist: get/create user and session, log, daily trend
    try:
        with db_cursor() as cur:
            uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
            session["user_uuid"] = _  # ensure it's set
            sid, _ = get_or_create_session(cur, uid)
            meta = {
                "risk_score": risk_score,
                "emotion_category": emotion_out["emotion_category"],
                "tone": emotion_out["tone"],
                "confidence": emotion_out["confidence"],
                "keyword_counts": risk_out.get("keyword_counts", {}),
                "is_crisis": crisis_out.get("is_crisis", False),
            }
            log_message(cur, sid, "user", text, meta)
            log_message(cur, sid, "assistant", advice_out.get("advice", "") + " " + " ".join(advice_out.get("steps", [])), {"meta": meta})
            upsert_daily_trend(cur, uid, date.today().isoformat(), risk_score * 100, risk_score * 100)
    except Exception:
        pass  # run even without DB

    return _json_response({
        "risk_score": round(risk_score * 100, 1),
        "emotion_category": emotion_out["emotion_category"],
        "tone": emotion_out["tone"],
        "confidence": emotion_out["confidence"],
        "keyword_counts": risk_out.get("keyword_counts", {}),
        "advice": advice_out.get("advice", ""),
        "steps": advice_out.get("steps", []),
        "is_crisis": advice_out.get("is_crisis", False),
        "helpline_guidance": advice_out.get("helpline_guidance", []),
        "is_medical_advice": False,
    })


# --- Voice (stub): accept input, return mock. Does NOT crash. ---
@api_bp.route("/predict/voice", methods=["POST"])
def predict_voice():
    # Accept JSON { "audio_base64": "..." } or form; we do not process audio.
    _ = request.get_json() or request.form or {}
    return _json_response({
        "feature_under_development": True,
        "message": "Voice input is under development. Please use the Text tab for now.",
        "risk_score": 0,
        "emotion_category": "low",
        "tone": "neutral",
        "confidence": 0,
        "keyword_counts": {},
        "advice": "Your voice matters. Until this feature is ready, typing how you feel can be just as helpful.",
        "steps": ["Use the Text tab to share what's on your mind.", "Take your time—there's no rush."],
        "is_crisis": False,
        "helpline_guidance": [],
    })


# --- Image (stub): accept upload, return mock. Does NOT crash. ---
@api_bp.route("/predict/image", methods=["POST"])
def predict_image():
    # Accept form file "image" or JSON "image_base64"; we do not process image.
    _ = request.files.get("image") or request.get_json() or {}
    return _json_response({
        "feature_under_development": True,
        "message": "Image emotion detection is under development. Please use the Text tab for now.",
        "risk_score": 0,
        "emotion_category": "low",
        "tone": "neutral",
        "confidence": 0,
        "keyword_counts": {},
        "advice": "We're working on this. In the meantime, putting your feelings into words in the Text tab can be very helpful.",
        "steps": ["Switch to the Text tab.", "Describe what you're experiencing—even briefly."],
        "is_crisis": False,
        "helpline_guidance": [],
    })


# --- Contact form: validate, store, optional email to admin. ---
@api_bp.route("/contact", methods=["POST"])
def contact_submit():
    data = request.get_json() or request.form or {}
    topic = (data.get("topic") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()
    err = []
    if not topic or len(topic) > 100:
        err.append("Please choose a topic.")
    if not email:
        err.append("Email is required.")
    elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", email) or len(email) > 255:
        err.append("Please enter a valid email.")
    if not message or len(message) > 10000:
        err.append("Message is required (max 10000 characters).")
    if err:
        return _json_response({"ok": False, "errors": err}), 400
    try:
        with db_cursor() as cur:
            save_contact_submission(cur, topic, email, message)
    except Exception:
        return _json_response({"ok": False, "errors": ["Could not save. Try again later."]}), 500
    em_ok, em_err = send_contact_notification(topic, email, message)
    return _json_response({"ok": True, "email_sent": em_ok})


# --- MCQ: GET questions, POST submit and get score/severity. ---
@api_bp.route("/mcq", methods=["GET"])
def mcq_questions():
    t = (request.args.get("type") or "stress").lower()
    if t not in ("stress", "anxiety", "depression"):
        t = "stress"
    items = get_mcq(t)
    return _json_response({"assessment_type": t, "questions": items})


@api_bp.route("/mcq", methods=["POST"])
def mcq_submit():
    data = request.get_json() or request.form or {}
    t = (data.get("type") or "stress").lower()
    if t not in ("stress", "anxiety", "depression"):
        t = "stress"
    answers = data.get("answers")
    if not isinstance(answers, list):
        answers = []
    result = score_mcq(t, answers)
    try:
        with db_cursor() as cur:
            uid = None
            try:
                uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
                session["user_uuid"] = _
            except Exception:
                pass
            save_assessment_result(
                cur, uid, t, result["total_score"], result["severity"],
                json.dumps({"answers": answers, "per_question": result.get("per_question", [])}),
            )
    except Exception:
        pass
    return _json_response(result)
