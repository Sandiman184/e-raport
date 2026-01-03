from flask import Blueprint

grades_bp = Blueprint('grades', __name__)

from . import routes
