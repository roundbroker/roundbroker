# encoding: utf-8

import os

class Config(object):

    # Consider that the directory of the main script is the APP_DIR
    APP_DIR = os.environ.get('APP_DIR', os.getcwd())

    # Public URLs
    HOOK_ROOT_URL = "http://de1b6d5a.ngrok.io/hook"

    # Secret key
    SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'This is NOT a great secret !')    

    # Listen host and port
    LISTEN_HOST = os.environ.get('APP_LISTEN_HOST', '127.0.0.1')
    LISTEN_PORT = int(os.environ.get('APP_LISTEN_PORT', 8000))

    # Sql alchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get("APP_SQLALCHEMY_URI", 'sqlite:///' + os.path.join(APP_DIR, 'app-dev.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
    
    # Github OAuth
    GITHUB_CLIENT_ID = "b1424e2f1cd4e9c2eeb9"
    GITHUB_CLIENT_SECRET = "e6f31f1fcf6df58eca73b9aaf74f2c240a8d2815"
    
    # Nchan URIs
    NCHAN_PUBLISH_ROOT_URL = "http://127.0.0.1:8081/pub"
    NCHAN_SUBSCRIBE_ROOT_URL = "http://127.0.0.1:8081/sub"    

    # Debug variables
    EXPLAIN_TEMPLATE_LOADING = True
