# app/fetcher.py
from flask import Flask, request, jsonify
from .utils import fetch_and_store_chunk

app = Flask(__name__)

@app.route('/fetch', methods=['GET'])
def fetch_chunk():
    video = request.args.get('video')
    chunk = request.args.get('chunk', type=int)
    if not video or chunk is None:
        return jsonify({'error': 'Missing parameters'}), 400

    result = fetch_and_store_chunk(video, chunk)
    return jsonify({'status': result})
