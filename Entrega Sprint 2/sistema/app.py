import os
import secrets
from pathlib import Path
from flask import Flask
from models import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=str(Path(__file__).with_name('sistema.sqlite3')),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=16384)
    if test_config:
        app.config.update(test_config)
    app.teardown_appcontext(close_db)
    from controllers import routes
    app.register_blueprint(routes)
    from commands import register_commands
    register_commands(app)
    with app.app_context():
        init_db()
    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5000)
