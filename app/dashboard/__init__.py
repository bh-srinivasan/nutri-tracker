from flask import Blueprint

bp = Blueprint('dashboard', __name__)

# Import routes to register them with the blueprint
from app.dashboard import routes
