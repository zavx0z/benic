from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO

from app.shared.models import db
from config import Config

APP_ROOT = Path(__file__).parents[1]
dotenv_path = APP_ROOT / '.env'
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config.from_object(Config)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
db.init_app(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()
migrate = Migrate(app, db)

CORS(app, supports_credentials=True, expose_headers=["Content-Disposition"])
# API ------------------------------------------
from app.api import api

app.register_blueprint(api, url_prefix='/api')
# TASK ------------------------------------------
from app.task import task
from app.task.models import *

app.register_blueprint(task, url_prefix='/api')
# TAG ------------------------------------------
from app.tag import tag
from app.tag.models import *

app.register_blueprint(tag, url_prefix='/api')
# VIDEO ------------------------------------------
from app.video import video
from app.video.models import *

app.register_blueprint(video, url_prefix='/api')
# PERIOD ------------------------------------------
from app.period import period
from app.period.models import *

app.register_blueprint(period, url_prefix='/api')
# INTERNAL ------------------------------------------
from app.internal import internal

app.register_blueprint(internal, url_prefix='/internal')
# AUTH ------------------------------------------
from app.auth import authenticate
from app.auth.models import *

app.register_blueprint(authenticate, url_prefix='/api/auth')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
