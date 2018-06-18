# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint(
    'web', __name__,
    url_prefix='/',
    static_url_path='/',
    template_folder='templates',
    static_folder='static')

from . import resources

from flask import g
from roundbroker.extensions import github

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token
