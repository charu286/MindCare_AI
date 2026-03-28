# MindCare AI - Flask application factory
# Python-first, self-hosted. All logic in Python.

from pathlib import Path
from flask import Flask
from flask_cors import CORS

from app.config import Config, BASE_DIR, ROOT_DIR

def create_app(config=None):
    app = Flask(
        __name__,
        template_folder=str(ROOT_DIR / "templates"),
        static_folder=str(ROOT_DIR / "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    CORS(app, supports_credentials=True)

    from app.routes.page_routes import page_bp
    from app.routes.chat_routes import chat_bp
    from app.routes.api_routes import api_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(page_bp)
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.context_processor
    def inject_disclaimer():
        from app.config import DISCLAIMER_TEXT
        return {"disclaimer_text": DISCLAIMER_TEXT}

    return app


# For WSGI: gunicorn "app:app"
app = create_app()
