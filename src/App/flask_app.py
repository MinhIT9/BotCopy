# BOTCOPY/src/App/flask_app.py

from App import create_app

def run_flask():
    app = create_app()
    app.run(debug=True, use_reloader=False)
