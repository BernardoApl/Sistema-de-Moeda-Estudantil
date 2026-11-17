import os
import secrets
from pathlib import Path
from flask import Flask
from models import close_db, init_db


def create_app(test_config=None, app=None):
    app = app or Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE_URL=os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING'),
                      DATABASE=str(Path(__file__).with_name('sistema.sqlite3')),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=16384)
    if test_config:
        app.config.update(test_config)
    app.teardown_appcontext(close_db)
    from controllers import routes
    app.register_blueprint(routes)
    from commands import register_commands
    register_commands(app)
    if not app.config['DATABASE_URL']:
        with app.app_context():
            init_db()
    return app


app = Flask(__name__)
create_app(app=app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
