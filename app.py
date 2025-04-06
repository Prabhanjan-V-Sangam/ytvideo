from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from redispython import store_video_in_redis  # <-- Correct import

import threading  # For optional async push

app = Flask(__name__)

NGINX_URL = "http://192.168.1.8:8081/videos/"  # Load videos via NGINX

@app.route("/")
def index():
    try:
        response = requests.get(NGINX_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching videos: {e}", 500

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract video links
    video_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href") and link.get("href").lower().endswith((".mp4", ".webm", ".mkv", ".avi", ".mov"))
    ]

    return render_template("index.html", video_files=video_files, nginx_url=NGINX_URL)

@app.route("/watch/<video_name>")
def watch(video_name):
    # Trigger Redis chunking in background
    threading.Thread(target=store_video_in_redis, args=(video_name,)).start()

    return render_template("watch.html", video_url=f"{NGINX_URL}{video_name}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
