from flask import Blueprint

bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api import routes
