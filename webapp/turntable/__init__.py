# encoding: utf-8

from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)
    app.config.from_object('turntable.settings.Config')

    # Initialize extensions
    from turntable.extensions import db
    db.init_app(app)

    from turntable.extensions import migrate
    migrate.init_app(app, db)

    from turntable.extensions import github
    github.init_app(app)

    # Initialize blueprints

    # UI
    from turntable.web import blueprint as blueprint_ui
    app.register_blueprint(blueprint_ui)

    # Produce
    from turntable.produce import blueprint as blueprint_produce
    app.register_blueprint(blueprint_produce)

    # Nchan-cb
    from turntable.nchancb import blueprint as blueprint_nchancb
    app.register_blueprint(blueprint_nchancb)

    return app

