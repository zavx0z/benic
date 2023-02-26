import os

from dotenv import load_dotenv

APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)
from app import socketio, app

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    if os.getenv('DEBUG'):
        host = 'localhost'
        print(f'run develop server {host}:{port}')
        socketio.run(
            app,
            host=host,
            port=port,
            debug=True,
            log_output=True,
        )
    else:
        socketio.run(app, host=host, port=port)
