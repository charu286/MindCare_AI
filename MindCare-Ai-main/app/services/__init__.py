# MindCare AI - Services (emotion, risk, safety, advice)
# All logic in Python.

from app.services.risk_engine import compute_risk
from app.services.emotion_engine import analyze_emotion
from app.services.safety_engine import check_crisis
from app.services.advice_engine import generate_advice

__all__ = ["compute_risk", "analyze_emotion", "check_crisis", "generate_advice"]
