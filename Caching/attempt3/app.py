from flask import Flask, request, jsonify, render_template_string, Response
from services.addtoredis import store_video_in_redis
from services.showfromredis import get_playlist, get_ts_chunk
import redis

REDIS_HOST = "192.168.1.8"
REDIS_PORT = 6379

redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=0, 
    username="default", 
    password="user", 
    decode_responses=True
)

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Video List</title></head>
<body>
    <h1>Available Videos</h1>
    <ul>
        {% for video in videos %}
            <li><a href="/video/{{ video }}">{{ video }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def list_videos():
    videos = redis_client.lrange("video:list", 0, -1)
    return render_template_string(HTML_TEMPLATE, videos=videos)

@app.route("/video/<path:video_id>")
def serve_playlist(video_id):
    playlist = get_playlist(video_id)
    if playlist:
        return playlist, 200, {'Content-Type': 'application/vnd.apple.mpegurl'}

    result = store_video_in_redis(video_id)
    if result == "Video stored in Redis":
        playlist = get_playlist(video_id)
        return playlist, 200, {'Content-Type': 'application/vnd.apple.mpegurl'}
    return jsonify({"error": "Video not found"}), 404
'''
@app.route("/video/<path:video_id>/chunk/<chunk_num>")
def serve_ts(video_id, chunk_num):
    response = get_ts_chunk(video_id, chunk_num)
    if response:
        return response
    return jsonify({"error": "Chunk not found"}), 404
'''
@app.route("/video/<path:video_id>/index.m3u8")
def serve_m3u8(video_id):
    m3u8 = get_m3u8(video_id)
    if m3u8:
        return Response(m3u8, mimetype="application/vnd.apple.mpegurl")
    return jsonify({"error": "Playlist not found"}), 404

@app.route("/video/<path:video_id>/chunk/<int:chunk_num>")
def serve_ts(video_id, chunk_num):
    chunk = get_ts_chunk(video_id, chunk_num)
    if chunk:
        return Response(chunk, mimetype="video/MP2T")
    return jsonify({"error": "Chunk not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
