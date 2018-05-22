# encoding: utf-8

from flask import g
from flask_github import GitHub

github = GitHub()

def configure_auth(app):
    github.init_app(app)

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token
