# encoding : utf-8

from flask import Blueprint

blueprint = Blueprint('pivot', __name__, url_prefix='/pivot')

from . import resources
