from flask import Blueprint

bp = Blueprint('admin', __name__)

# Import routes to register them with the blueprint
from app.admin import routes
