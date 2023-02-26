from flask import Blueprint
from flask_cors import CORS

tag = Blueprint('tag', __name__)
CORS(tag)
from app.tag import routes
