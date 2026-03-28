# MindCare AI - Risk scoring (Python only)
# risk_score = min(1.0, keyword_factor*0.5 + length_factor*0.2 + intensity_factor*0.3)
# Handles: negations ("not stressed"), repeated keyword damping, English + Hindi.

import re
import math

# English negative/positive stress/anxiety/depression keywords (lowercase)
EN_NEGATIVE = {
    "stress", "stressed", "stressful", "stressing", "anxiety", "anxious", "anxiousness",
    "depress", "depression", "depressed", "depressing", "sad", "sadness", "hopeless",
    "hopelessness", "angry", "anger", "fear", "fearful", "scared", "worry", "worried",
    "overwhelm", "overwhelmed", "panic", "panicking", "suicidal", "suicide", "kill",
    "self-harm", "self harm", "hurt myself", "end it", "give up", "cant go on",
    "cant take it", "cant take this", "tired", "exhausted", "lonely", "loneliness",
    "empty", "numb", "worthless", "useless", "failure", "guilty", "guilt", "shame",
}
# Hindi (romanized) equivalents
HI_NEGATIVE = {
    "tension", "tenshan", "chinta", "udaas", "nirash", "ghabrahat", "dar",
    "takleef", "preshan", "dukh", "dukhi", "bechain", "thakaan", "thaka",
    "tanav", "chintit", "nirasha",
}
# Negation patterns
NEGATION = re.compile(
    r"\b(not|no|never|neither|n't|don't|doesn't|didn't|won't|wouldn't|can't|cannot|isn't|aren't|wasn't|weren't|haven't|hasn't|hadn't|ain't)\s+(\w+)",
    re.I,
)
# Intensity amplifiers
INTENSITY_WORDS = {
    "very", "extremely", "really", "so", "too", "incredibly", "absolutely",
    "totally", "completely", "utterly", "deeply", "highly", "bahut", "zyada",
    "bilkul", "kaafi",
}

def _tokenize(text):
    if not text or not isinstance(text, str):
        return []
    return re.findall(r"\b\w+\b", text.lower())

def _count_negations(tokens):
    """Find negated positive/negative terms. Negation flips or dampens."""
    s = " ".join(tokens)
    hits = 0
    for m in NEGATION.finditer(s):
        w = m.group(2).lower()
        if w in EN_NEGATIVE or w in HI_NEGATIVE:
            hits += 1
    return hits

def _keyword_factor(tokens):
    """0..1. Negative keywords increase; negations dampen; repetition dampens."""
    seen = set()
    score = 0.0
    negations = _count_negations(tokens)
    for t in tokens:
        if t in EN_NEGATIVE or t in HI_NEGATIVE:
            # Damping: first occurrence 1.0, next 0.7, then 0.5, etc.
            mult = 1.0 if t not in seen else 0.6
            seen.add(t)
            score += 0.25 * mult
    # Cap raw and apply negation damping: each negation reduces effect
    raw = min(1.0, score)
    negation_damp = 1.0 / (1.0 + 0.5 * negations)
    return min(1.0, raw * negation_damp)

def _length_factor(text):
    """Longer, more detailed text can indicate higher engagement. 0..1."""
    n = len(text or "") if text else 0
    if n <= 50:
        return 0.1
    if n <= 200:
        return 0.3 + 0.3 * min(1.0, (n - 50) / 150)
    if n <= 800:
        return 0.6 + 0.3 * min(1.0, (n - 200) / 600)
    return 0.9 + 0.1 * min(1.0, (n - 800) / 500)

def _intensity_factor(tokens):
    """Presence of intensity words near negative terms. 0..1."""
    intensity_count = sum(1 for t in tokens if t in INTENSITY_WORDS)
    neg_count = sum(1 for t in tokens if t in EN_NEGATIVE or t in HI_NEGATIVE)
    if neg_count == 0:
        return 0.1
    # More intensity words and negative words -> higher
    combined = min(1.0, (intensity_count * 0.15) + (min(neg_count, 5) * 0.12))
    return combined

def compute_risk(text):
    """
    Returns a dict: risk_score (0.0–1.0), keyword_factor, length_factor, intensity_factor,
    and keyword_counts (dict of term -> count for EN+HI negative terms).
    """
    tokens = _tokenize(text)
    kf = _keyword_factor(tokens)
    lf = _length_factor(text)
    iff = _intensity_factor(tokens)
    risk = min(1.0, (kf * 0.5) + (lf * 0.2) + (iff * 0.3))

    keyword_counts = {}
    for t in tokens:
        if t in EN_NEGATIVE or t in HI_NEGATIVE:
            keyword_counts[t] = keyword_counts.get(t, 0) + 1

    return {
        "risk_score": round(risk, 4),
        "keyword_factor": round(kf, 4),
        "length_factor": round(lf, 4),
        "intensity_factor": round(iff, 4),
        "keyword_counts": keyword_counts,
    }
