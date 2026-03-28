# MindCare AI - MCQ-based assessment. Score and classify severity.
# Not a clinical tool; for awareness only.

# Each item: question, options (list of {text, score})
MCQ_STRESS = [
    {"q": "In the past week, how often have you felt nervous or stressed?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you found it hard to wind down?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt that you couldn't cope with all you had to do?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you been upset because of something that happened unexpectedly?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt that difficulties were piling up so high you could not overcome them?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
]
MCQ_ANXIETY = [
    {"q": "In the past two weeks, how often have you felt nervous, anxious, or on edge?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you not been able to stop or control worrying?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you worried too much about different things?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you had trouble relaxing?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt so restless that it was hard to sit still?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
]
MCQ_DEPRESSION = [
    {"q": "In the past two weeks, how often have you had little interest or pleasure in doing things?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt down, depressed, or hopeless?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you had trouble falling or staying asleep, or sleeping too much?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt tired or had little energy?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
    {"q": "How often have you felt bad about yourself—or that you are a failure or have let yourself or your family down?", "opts": [("Not at all", 0), ("Several days", 1), ("More than half the days", 2), ("Nearly every day", 3)]},
]

MCQ = {"stress": MCQ_STRESS, "anxiety": MCQ_ANXIETY, "depression": MCQ_DEPRESSION}
MAX_SCORE = 15  # 5 * 3

# Severity bands (0–15): minimal 0-4, mild 5-9, moderate 10-12, severe 13-15
def _severity(score: int) -> str:
    if score <= 4:
        return "minimal"
    if score <= 9:
        return "mild"
    if score <= 12:
        return "moderate"
    return "severe"


def get_mcq(assessment_type: str) -> list:
    return MCQ.get(assessment_type, []) or MCQ["stress"]


def score_mcq(assessment_type: str, answers: list[int]) -> dict:
    """answers: list of chosen option index per question. Returns total_score, severity, per_question (for labels)."""
    items = get_mcq(assessment_type)
    if len(answers) != len(items):
        answers = answers[: len(items)] + [0] * (len(items) - len(answers))
    total = 0
    per_q = []
    for i, (item, a) in enumerate(zip(items, answers)):
        opt_idx = min(max(int(a), 0), len(item["opts"]) - 1)
        s = item["opts"][opt_idx][1]
        total += s
        per_q.append({"question": item["q"], "score": s, "max": 3})
    return {
        "total_score": total,
        "max_score": MAX_SCORE,
        "severity": _severity(total),
        "assessment_type": assessment_type,
        "per_question": per_q,
    }
