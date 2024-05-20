# BOTCOPY/src/App/flask_app.py

from flask import Flask, session

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  # Thay đổi thành khóa bí mật của bạn
    from .routes import main
    app.register_blueprint(main)
    return app

app = create_app()  # Tạo app ở mức toàn cục

def run_flask():
    app.run(debug=True, use_reloader=False)
