# MindCare AI - Crisis safety logic (Python only)
# If self-harm/suicide ideation: override advice, encourage real human, helpline, never imply AI is sufficient.

import re

# Crisis indicators (lowercase); avoid overly broad terms.
CRISIS_PATTERNS = [
    r"\bkill\s+(my)?self\b",
    r"\bend\s+(my\s+)?life\b",
    r"\bsuicid(e|al)\b",
    r"\bself\s*[- ]?harm\b",
    r"\bhurt\s+(my)?self\b",
    r"\bcut\s+(my)?self\b",
    r"\bhanging\s+(my)?self\b",
    r"\bdon'?t\s+want\s+to\s+live\b",
    r"\bwant\s+to\s+die\b",
    r"\bbetter\s+off\s+dead\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\bapna\s+ghar\s+khatam\b",  # Hindi-romanized examples
    r"\bjeene\s+ka\s+mana\b",
    r"\bkhudkushi\b",
    r"\bkhud\s+ko\s+nuksan\b",
]
COMPILED = [re.compile(p, re.I) for p in CRISIS_PATTERNS]

# Helpline copy (non-medical; encourage professional help)
CRISIS_RESPONSE = {
    "is_crisis": True,
    "override_advice": True,
    "message": (
        "It sounds like you may be going through something very difficult. "
        "MindCare AI is not a medical professional and cannot replace human support. "
        "Please consider reaching out to a trusted person or a crisis helpline. "
        "You deserve to be heard by someone who can be there for you."
    ),
    "helpline_guidance": [
        "India: Vandrevala Foundation 1860-2662-345 / 1800-2333-330; iCall 022-2552-1111",
        "International: Befrienders Worldwide https://www.befrienders.org",
        "If you are in immediate danger, please contact emergency services or go to your nearest hospital.",
    ],
}

def check_crisis(text):
    """
    If crisis indicators found, return CRISIS_RESPONSE (with is_crisis True).
    Otherwise return {"is_crisis": False, "override_advice": False}.
    """
    if not text or not isinstance(text, str):
        return {"is_crisis": False, "override_advice": False}
    t = text.lower()
    for rx in COMPILED:
        if rx.search(t):
            return dict(CRISIS_RESPONSE)
    return {"is_crisis": False, "override_advice": False}
