# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint('hook', __name__, url_prefix='/hook')

from . import resources
