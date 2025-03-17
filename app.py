from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NGINX_URL = "http://192.168.1.8:8081/videos/"  # Load videos via Nginx reverse proxy cache

@app.route("/")
def index():
    response = requests.get("http://192.168.1.8:8080/")  # Fetch from original server
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract video links
    video_files = [
        link.get("href")
        for link in soup.find_all("a")
        if link.get("href").endswith((".mp4", ".webm", ".mkv", ".avi", ".mov"))
    ]

    return render_template("index.html", video_files=video_files, nginx_url=NGINX_URL)


@app.route("/watch/<video_name>")
def watch(video_name):
    return render_template("watch.html", video_url=f"{NGINX_URL}{video_name}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
