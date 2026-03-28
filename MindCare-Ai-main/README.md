# MindCare AI

A **production-style, Python-first, self-hosted** emotional support and awareness platform. It is **not** a medical system and does not replace therapy, diagnosis, or professional mental-health care.

https://raginikp.github.io/MindCare-Ai/

## Stack

- **Backend:** Python 3.10+, Flask, Flask-CORS, mysql-connector-python  
- **Frontend:** Jinja2, HTML5, CSS3, vanilla JavaScript  
- **Database:** MySQL 8+

## Setup

1. **Python 3.10+**

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. **MySQL 8+**

   - Create DB and user, then run:

   ```bash
   mysql -u root -p < db/schema.sql
   ```

   - Configure via environment (optional):

   - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`  
   - `SECRET_KEY` for Flask sessions  
   - Contact email (optional): `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `ADMIN_EMAIL`

3. **Run**

   ```bash
   python run.py
   ```

   Or: `gunicorn -w 4 -b 0.0.0.0:5000 "app:app"` (using `app.py`’s `app`).

   Open: `http://localhost:5000`

## Auth (optional, hybrid)

- **Anonymous (default):** Test, Chat, Dictionary work without login; data tied to a temporary session.
- **Login / Register:** For saved history, dashboard trends, and contact follow-ups. Session-based (Flask session). Passwords hashed with Werkzeug. When an anon user registers or logs in, their session data is migrated to the account. Non-forceful: “Create an account only if you want to save your progress.”

## Pages

- **Home** – Hero, Stress/Anxiety/Depression cards, sticky notes, “When to seek help”, Did You Know. Lighter, welcoming; no comparison table (moved to Dictionary).  
- **Test** – **AI-Based:** Text (full), Voice and Image (“Coming soon” stubs); **MCQ:** Stress/Anxiety/Depression with score, severity, Chart.js.  
- **Chat** – Multi-turn, context-aware, empathy-first; safety always on.  
- **Dictionary** – **Split-screen (top):** Left = Mental Health Concepts (Stress, Anxiety, Depression, Burnout, Panic Attack, PTSD, Social Anxiety); Right = Phobias & Fears (Nyctophobia, Claustrophobia, Social Phobia, Thanatophobia, etc.). **Separator:** “Understanding emotions also means understanding fears.” **Bottom:** Stress vs Anxiety vs Depression table.  
- **Dashboard** – 7-day avg/peak stress, session count, Chart.js bar chart.  
- **Contact** – Warm intro, topic + email + message; validation; DB store; optional email to admin; calm UI.  

## API

- **POST /api/v1/predict** – Text analysis. `{"text":"..."}` → risk, emotion, tone, advice, steps, crisis/helplines.  
- **POST /api/v1/predict/voice** – Stub; returns `feature_under_development` and a calm message.  
- **POST /api/v1/predict/image** – Stub; same.  
- **POST /api/v1/contact** – `{topic, email, message}`; validation; DB store; optional email to admin.  
- **GET /api/v1/mcq?type=stress|anxiety|depression** – Questions for MCQ.  
- **POST /api/v1/mcq** – `{type, answers: [0,1,...]}` → `total_score`, `severity`, `per_question`.  
- **GET /chat/history** – Recent messages for multi-turn.  
- **POST /chat/message** – `{"text":"..."}` → `reply`, `is_crisis`.  
- All JSON responses include `"is_medical_advice": false`.

## Disclaimer

Shown on Home, Test, and in crisis flows:

> MindCare AI is not a medical professional and does not replace therapy, diagnosis, or professional mental-health care.

## Theme

- Light and dark calm pastel modes  
- Toggle in navbar; preference stored in `localStorage` (`mindcare-theme`)

## Database

- `users` (with `email`, `password_hash`, `is_anonymous` for auth), `sessions`, `conversation_history`, `daily_trends`, `mental_health_terms`, `coping_strategies`, `resources`, `contact_submissions`, `fears_phobias`, `assessment_results`  
- See `db/schema.sql`. For **existing** DBs, run `db/migrations/001_add_auth_columns.sql` to add auth columns to `users`.

## Licence

Use and modify as needed for your deployment.

