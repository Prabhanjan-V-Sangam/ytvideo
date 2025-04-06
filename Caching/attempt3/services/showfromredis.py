# services/showfromredis.py
import redis
from flask import Response, jsonify

REDIS_HOST = "192.168.1.8"
REDIS_PORT = 6379

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username="default",
    password="user"
)

def get_m3u8_playlist(video_id):
    playlist = redis_client.hget(f"video:{video_id}:m3u8", "playlist")
    if playlist:
        return Response(playlist, mimetype="application/vnd.apple.mpegurl")
    return jsonify({"error": "Playlist not found"}), 404

def get_ts_chunk(video_id, chunk_num):
    chunk = redis_client.get(f"video:{video_id}:chunk:{chunk_num}")
    if chunk:
        return Response(chunk, mimetype="video/mp2t")
    return None
