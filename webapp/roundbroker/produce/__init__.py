# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint('produce', __name__, url_prefix='/p')

from . import resources
