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
    from turntable.web import blueprint
    app.register_blueprint(blueprint)

    from turntable.pivot import blueprint
    app.register_blueprint(blueprint)

    return app

