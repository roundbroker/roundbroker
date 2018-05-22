# encoding: utf-8

import os
from flask import Flask
from werkzeug.utils import import_string

from app.web import blueprint as web_blueprint
from app.hook import blueprint as hook_blueprint
from app.ext.sqlalchemy import configure_db
from app.ext.github import configure_auth

class FlaskServer(object):

    def __init__(self, import_name=__name__):
        self.app_settings = os.getenv('APP_SETTINGS', 'app.settings.Config')
        self.app = Flask(import_name)
        self.app.config.from_object(import_string(self.app_settings))

        self.register_extensions()
        self.register_blueprints()

    def run(self):
        listen_host = self.app.config.get('LISTEN_HOST')
        listen_port = self.app.config.get('LISTEN_PORT')

        self.app.run(
            host=listen_host,
            port=listen_port,
            debug=True)

    def register_extensions(self):
        self.app.logger.info('Registering the extensions')
        # configure sql database
        configure_db(self.app)

        # configure auth via github
        configure_auth(self.app)

    def register_blueprints(self):
        self.app.logger.info('Registering the blueprints')
        self.app.register_blueprint(hook_blueprint)
        self.app.register_blueprint(web_blueprint)

    def stop(self):
        self.app.logger.info('Stoping the server')
