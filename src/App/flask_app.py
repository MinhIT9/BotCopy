# BOTCOPY/src/App/flask_app.py

from flask import Flask

def create_app():
    app = Flask(__name__)
    # Đăng ký blueprint tại đây
    from .routes import main
    app.register_blueprint(main)
    return app

app = create_app()  # Tạo app ở mức toàn cục

def run_flask():
    app.run(debug=True, use_reloader=False)
