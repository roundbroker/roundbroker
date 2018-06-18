# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint('nchancb', __name__, url_prefix='/nchan-cb')

from . import resources
