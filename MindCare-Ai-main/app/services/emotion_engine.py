# MindCare AI - Emotion and tone analysis (Python only)
# Emotion category: high / medium / low. Tone: sad, anxious, angry, calm, happy, neutral.

import re

TONES = ["sad", "anxious", "angry", "calm", "happy", "neutral"]

# Tone keyword groups (lowercase)
TONE_MAP = {
    "sad": {"sad", "sadness", "cry", "crying", "tear", "hopeless", "empty", "lonely", "grief", "loss", "dukh", "udaas", "dukhi"},
    "anxious": {"anxiety", "anxious", "worry", "worried", "nervous", "panic", "fear", "scared", "stress", "stressed", "ghabrahat", "chinta", "bechain", "dar"},
    "angry": {"angry", "anger", "furious", "rage", "irritated", "frustrated", "annoyed", "gussa", "krodh"},
    "calm": {"calm", "peaceful", "relaxed", "serene", "shant", "sukun"},
    "happy": {"happy", "joy", "glad", "pleased", "good", "fine", "better", "khush", "acha"},
    "neutral": set(),
}

def _tokenize(text):
    if not text or not isinstance(text, str):
        return []
    return re.findall(r"\b\w+\b", text.lower())

def _tone_scores(tokens):
    scores = {t: 0.0 for t in TONES}
    for t in tokens:
        for tone, words in TONE_MAP.items():
            if tone != "neutral" and t in words:
                scores[tone] += 1.0
    # If no tone words, boost neutral
    if sum(scores.values()) == 0:
        scores["neutral"] = 1.0
    return scores

def _emotion_category(risk_score):
    """ high / medium / low from risk 0–1 """
    if risk_score >= 0.65:
        return "high"
    if risk_score >= 0.35:
        return "medium"
    return "low"

def _confidence(risk_score, tone_scores):
    """ 0..1. Higher when one tone dominates and risk is consistent. """
    total = sum(tone_scores.values()) or 1.0
    max_share = max(tone_scores.values()) / total
    # More decisive tone + clear risk band -> higher confidence
    base = 0.5 + 0.3 * max_share
    if risk_score >= 0.6 or risk_score <= 0.25:
        base += 0.1
    return min(1.0, round(base, 2))

def analyze_emotion(text, risk_score):
    """
    Returns: emotion_category (high/medium/low), tone (one of TONES), confidence (0–1).
    """
    tokens = _tokenize(text)
    tone_scores = _tone_scores(tokens)
    tone = max(TONES, key=lambda t: tone_scores[t])
    cat = _emotion_category(risk_score)
    conf = _confidence(risk_score, tone_scores)
    return {
        "emotion_category": cat,
        "tone": tone,
        "confidence": conf,
    }
