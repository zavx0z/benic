from flask import Blueprint
from flask_cors import CORS

task = Blueprint('task', __name__)
CORS(task)
