from flask import Blueprint
from flask_cors import CORS

video = Blueprint('video', __name__)
CORS(video)
from app.video import routes
