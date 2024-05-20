# BOTCOPY/src/App/flask_app.py

from flask import Flask

def create_app():
    app = Flask(__name__)
    # Cấu hình và đăng ký các blueprints hoặc extensions ở đây nếu có
    return app

app = create_app()  # Tạo app ở mức toàn cục

def run_flask():
    app.run(debug=True, use_reloader=False)