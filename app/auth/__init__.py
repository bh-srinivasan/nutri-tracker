from flask import Blueprint

bp = Blueprint('auth', __name__)

# Import routes to register them with the blueprint
from app.auth import routes
