# MindCare AI - Page routes: Home, Test, Dictionary, Dashboard, Contact

from flask import Blueprint, render_template, session

page_bp = Blueprint("page", __name__)

@page_bp.route("/")
def home():
    return render_template("index.html")

@page_bp.route("/test")
def test():
    return render_template("test.html")

# Default concepts for Dictionary left panel (Stress, Anxiety, Depression, Burnout, Panic Attack, PTSD, Social Anxiety)
CONCEPTS_DEFAULT = [
    {"term": "Stress", "definition": "Your body's response to demands. Common and manageable with simple coping strategies."},
    {"term": "Anxiety", "definition": "Persistent worry or fear about the future or uncertainty. Grounding techniques can help."},
    {"term": "Depression", "definition": "Low mood and loss of interest that can affect daily life. Small steps and support help."},
    {"term": "Burnout", "definition": "Exhaustion from prolonged stress, often work-related. Rest and boundaries are important."},
    {"term": "Panic Attack", "definition": "Sudden, intense fear with physical symptoms. They usually pass; breathing exercises can help in the moment."},
    {"term": "PTSD", "definition": "A response to trauma. Flashbacks, avoidance, and hypervigilance are common. Professional support helps."},
    {"term": "Social Anxiety", "definition": "Intense fear of being judged in social situations. Very common. Gradual exposure and self-compassion help."},
]
# Default phobias for Dictionary right panel
FEARS_DEFAULT = [
    {"name": "Nyctophobia", "meaning": "Fear of darkness", "description": "Fear or discomfort in dark or low-light settings. Soft lighting and small steps can ease it.", "emoji_or_icon": "🌙"},
    {"name": "Claustrophobia", "meaning": "Fear of enclosed spaces", "description": "Discomfort in elevators or crowded rooms. Breathing and knowing exits can reduce anxiety.", "emoji_or_icon": "📦"},
    {"name": "Social Phobia", "meaning": "Fear of social situations", "description": "Worry about being judged in social settings. Small, repeated exposure and self-compassion help.", "emoji_or_icon": "👥"},
    {"name": "Thanatophobia", "meaning": "Fear of death or dying", "description": "Anxiety about death or the process of dying. Talking with someone you trust can help.", "emoji_or_icon": "🕊️"},
    {"name": "Acrophobia", "meaning": "Fear of heights", "description": "Unease on bridges or near edges. Gradual exposure and breathing can help.", "emoji_or_icon": "⛰️"},
    {"name": "Agoraphobia", "meaning": "Fear of open or crowded spaces", "description": "Anxiety where escape feels difficult. Support and gradual practice help.", "emoji_or_icon": "🏙️"},
]


@page_bp.route("/dictionary")
def dictionary():
    terms = []
    fears = []
    try:
        from app.database import db_cursor, fetch_fears_phobias
        with db_cursor() as cur:
            try:
                cur.execute("SELECT term, definition, category FROM mental_health_terms ORDER BY sort_order, term")
                terms = cur.fetchall() or []
            except Exception:
                pass
            try:
                fears = fetch_fears_phobias(cur)
            except Exception:
                pass
    except Exception:
        pass
    # Build concepts: overlay DB terms on defaults so we always have all 7
    concepts = [dict(c) for c in CONCEPTS_DEFAULT]
    for t in terms:
        for i, c in enumerate(concepts):
            if c.get("term") == t.get("term"):
                concepts[i] = {**c, **t}
                break
    if not fears:
        fears = list(FEARS_DEFAULT)
    return render_template("dictionary.html", concepts=concepts, fears=fears)

@page_bp.route("/dashboard")
def dashboard():
    trends = []
    try:
        from app.database import db_cursor
        from datetime import date, timedelta
        with db_cursor() as cur:
            # Resolve user
            from app.database import get_or_create_user_uuid
            uid, _ = get_or_create_user_uuid(cur, session.get("user_uuid"))
            session["user_uuid"] = _
            # Last 7 days
            cur.execute(
                """SELECT date, avg_stress, peak_stress, session_count
                   FROM daily_trends WHERE user_id = %s AND date >= %s
                   ORDER BY date""",
                (uid, (date.today() - timedelta(days=7)).isoformat()),
            )
            trends = cur.fetchall() or []
    except Exception:
        pass
    # Aggregate for display
    avg_stress = 0.0
    peak_stress = 0.0
    session_count = 0
    if trends:
        avg_stress = sum(float(t.get("avg_stress") or 0) for t in trends) / len(trends)
        peak_stress = max((float(t.get("peak_stress") or 0) for t in trends), default=0)
        session_count = sum(int(t.get("session_count") or 0) for t in trends)
    return render_template("dashboard.html", trends=trends, avg_stress=round(avg_stress, 1), peak_stress=round(peak_stress, 1), session_count=session_count)

@page_bp.route("/contact")
def contact():
    return render_template("contact.html")
