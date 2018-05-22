# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint(
    'web', __name__,
    url_prefix='/ui',
    template_folder='templates',
    static_folder='static')

from . import resources
