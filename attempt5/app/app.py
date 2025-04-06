from flask import Flask, render_template, Response
import requests
from bs4 import BeautifulSoup
import redis
import threading
from redispython import store_video_in_redis  # your HLS + Redis logic

# Redis setup
redis_client = redis.StrictRedis(
    host="192.168.1.8",
    port=6379,
    db=0,
    username="default",
    password="user",
    decode_responses=False
)

app = Flask(__name__)

NGINX_URL = "http://192.168.1.8:8081/videos/"  # Video server base

@app.route("/")
def index():
    try:
        response = requests.get(NGINX_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching videos: {e}", 500

    soup = BeautifulSoup(response.text, "html.parser")
    video_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href") and link.get("href").lower().endswith((".mp4", ".webm", ".mkv", ".avi", ".mov"))
    ]
    return render_template("index.html", video_files=video_files, nginx_url=NGINX_URL)


@app.route("/playlist/<video_name>.m3u8")
def playlist(video_name):
    playlist = redis_client.get(f"video:{video_name}:playlist")
    if not playlist:
        return "Playlist not found", 404
    return Response(playlist, mimetype="application/vnd.apple.mpegurl")

@app.route("/chunk/<video_name>/<int:index>.ts")
def chunk(video_name, index):
    chunk_data = redis_client.hget(f"video:{video_name}:chunks", str(index))
    if chunk_data:
        return Response(chunk_data, mimetype="video/MP2T")
    return "Chunk not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
