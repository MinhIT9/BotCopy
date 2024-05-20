# BOTCOPY/src/App/__init__.py

from flask import Flask
from flask_bootstrap import Bootstrap  # type: ignore

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Thay đổi thành khóa bí mật của bạn
    Bootstrap(app)
    from .routes import main
    app.register_blueprint(main)
    return app
