# encoding: utf-8

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_db(app):
    db.app = app
    db.init_app(app)
    Migrate(app, db)
