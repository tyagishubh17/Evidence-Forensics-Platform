"""Flask application factory for the Review 1 prototype."""
import os

from flask import Flask, flash, redirect, url_for

from config import Config
from app.db import init_db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Tests pass their own settings (temporary folders and database).
    if test_config:
        app.config.update(test_config)

    # Make sure the storage folders exist.
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["TEST_COPY_FOLDER"], exist_ok=True)
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)

    init_db(app)

    from app.routes import bp, format_file_size
    app.register_blueprint(bp)

    @app.errorhandler(413)
    def file_too_large(error):
        limit = format_file_size(app.config["MAX_CONTENT_LENGTH"])
        flash(f"The file is too large. The maximum allowed size is {limit}.", "error")
        return redirect(url_for("main.index"))

    return app
