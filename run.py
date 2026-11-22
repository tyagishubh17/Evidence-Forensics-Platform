"""Start the Review 1 prototype with:  python run.py"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=False by default; set FLASK_DEBUG=1 to enable the debugger locally.
    app.run(host="127.0.0.1", port=5000)
