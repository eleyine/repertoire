from flask import Blueprint

bp = Blueprint('my_admin', __name__)

from app.admin import routes
