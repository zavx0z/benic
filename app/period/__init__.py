from flask import Blueprint
from flask_cors import CORS

period = Blueprint('period', __name__)
CORS(period)
from app.period import routes
