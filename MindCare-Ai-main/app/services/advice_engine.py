# MindCare AI - Empathetic advice (Python only)
# Empathy first, advice second. Validate, paraphrase, 3–5 CBT-style steps. Never dismiss, never diagnose.

import random

# Empathetic openers (warm, human; not robotic)
VALIDATE = [
    "I hear you.",
    "That makes sense.",
    "It’s understandable to feel that way.",
    "Thanks for sharing that with me.",
    "That sounds really hard.",
]

# When we have prior context (multi-turn), more continuous phrasing
VALIDATE_CONTEXT = [
    "Building on what you’ve shared—",
    "From what you’ve been saying—",
    "I’m with you on this.",
]

# Paraphrase templates (brief, natural)
PARAPHRASE = [
    "It sounds like {concern} is weighing on you.",
    "From what you’ve shared, {concern} seems to be affecting you.",
    "You’re dealing with a lot around {concern}.",
]
PARAPHRASE_CONTEXT = [
    "…and that’s a lot to carry.",
    "…and that can feel overwhelming.",
]

# CBT-style practical steps (never medical; phrased gently)
STEPS_POOL = [
    "Take a few slow breaths: inhale for 4, hold for 4, exhale for 6.",
    "Name one small thing you can control right now—and do just that.",
    "If you can, step outside or near a window for a few minutes.",
    "Write down three things that went okay today, however small.",
    "Reach out to one person you trust; a short message is enough.",
    "Do one gentle movement: stretch, walk around the room, or shake out your hands.",
    "Put on a song or sounds that usually calm you for 5 minutes.",
    "Remind yourself that feelings are temporary, even when they feel huge.",
    "Plan one small, pleasant activity for later today.",
    "If your thoughts are racing, try listing them on paper to create a bit of distance.",
]

def _short_concern(text, max_len=60):
    if not text or not isinstance(text, str):
        return "what's going on"
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 3].rsplit(maxsplit=1)[0] + "..."

def generate_advice(text, tone, emotion_category, is_crisis, crisis_payload=None, recent_messages=None):
    """
    If is_crisis and crisis_payload: return crisis message + helpline (no normal advice).
    Otherwise: validate, paraphrase, 3–5 CBT-style steps. Never dismiss, never diagnose.
    recent_messages: optional list of {role, content} for context-aware, human-like continuity.
    """
    if is_crisis and crisis_payload:
        return {
            "advice": crisis_payload.get("message", ""),
            "steps": [],
            "helpline_guidance": crisis_payload.get("helpline_guidance", []),
            "is_crisis": True,
        }
    concern = _short_concern(text)
    has_context = recent_messages and len(recent_messages) >= 2
    if has_context:
        validate = random.choice(VALIDATE_CONTEXT) + " " + random.choice(VALIDATE)
        para = random.choice(PARAPHRASE).format(concern=concern) + " " + random.choice(PARAPHRASE_CONTEXT)
    else:
        validate = random.choice(VALIDATE)
        para = random.choice(PARAPHRASE).format(concern=concern)
    n = random.randint(3, 5)
    steps = random.sample(STEPS_POOL, min(n, len(STEPS_POOL)))
    intro = "A few things that might help:" if has_context else "Here are some small steps that might help:"
    return {
        "advice": f"{validate} {para} {intro}",
        "steps": steps,
        "helpline_guidance": [],
        "is_crisis": False,
    }
