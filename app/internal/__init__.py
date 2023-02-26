from flask import Blueprint
from flask_cors import CORS

internal = Blueprint('internal', __name__)
CORS(internal)
from app.internal import routes
