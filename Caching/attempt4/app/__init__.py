# app/__init__.py

from flask import Flask
from .fetcher import fetch_chunk

def create_app():
    app = Flask(__name__)

    @app.route('/fetch', methods=['GET'])
    def fetch():
        return fetch_chunk()

    return app


