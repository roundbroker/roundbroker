# encoding: utf-8

from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)
    app.config.from_object('roundbroker.settings.Config')

    # Initialize extensions
    from roundbroker.extensions import db
    db.init_app(app)

    from roundbroker.extensions import migrate
    migrate.init_app(app, db)

    from roundbroker.extensions import github
    github.init_app(app)

    # Initialize blueprints

    # UI
    from roundbroker.web import blueprint as blueprint_ui
    app.register_blueprint(blueprint_ui)

    # Produce
    from roundbroker.produce import blueprint as blueprint_produce
    app.register_blueprint(blueprint_produce)

    # Nchan-cb
    from roundbroker.nchancb import blueprint as blueprint_nchancb
    app.register_blueprint(blueprint_nchancb)

    return app

