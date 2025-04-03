import redis
import requests

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username="default",  # Add username
    password="user",  # Add password
    decode_responses=False  # Set to False for binary data
)

def store_video_in_redis(video_name, video_url):
    # Fetch the video from the provided URL
    response = requests.get(video_url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {video_name}")
        return

    chunk_index = 0
    for chunk in response.iter_content(CHUNK_SIZE):
        redis_client.set(f"{video_name}:chunk:{chunk_index}", chunk)
        chunk_index += 1

    redis_client.set(f"{video_name}:total_chunks", chunk_index)
    print(f"Stored {video_name} in Redis ({chunk_index} chunks)")

# This will be called when we want to store a video in Redis
def store_video(video_name, video_url):
    store_video_in_redis(video_name, video_url)


'''
from flask import Flask, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

VIDEO_SERVER_URL = "http://localhost:8080/"
MASTER_API_URL = "http://localhost:5000/watch/"

@app.route("/")
def index():
    try:
        response = requests.get(VIDEO_SERVER_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching videos: {e}", 500

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract video links
    video_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href").endswith((".mp4", ".webm", ".mkv", ".avi", ".mov"))
    ]

    return render_template("index.html", video_files=video_files)

@app.route("/watch/<video_name>")
def watch(video_name):
    video_url = f"{MASTER_API_URL}{video_name}"
    # Check if the video is cached or available to stream
    response = requests.get(video_url)
    
    if response.status_code == 200:
        # Video found and ready to be streamed
        return render_template("watch.html", video_url=video_url)
    else:
        return f"Error fetching video: {video_name}", 404

@app.route("/cache_video/<video_name>", methods=["POST"])
def cache_video(video_name):
    # Trigger the cache_video endpoint in master-api to cache the video
    response = requests.post(f"http://localhost:5000/cache_video/{video_name}")
    
    if response.status_code == 200:
        return f"Video {video_name} is being cached.", 200
    else:
        return f"Failed to cache video {video_name}.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
'''