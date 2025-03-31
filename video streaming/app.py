from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

VIDEO_SERVER_URL = "http://host.docker.internal:8080/"
MASTER_API_URL = "http://master-api-service:5000/video/"

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
    return render_template("watch.html", video_url=video_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
