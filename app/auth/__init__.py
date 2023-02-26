from flask import Blueprint
from flask_cors import CORS

authenticate = Blueprint('auth', __name__)
CORS(authenticate)
from app.auth import routes
