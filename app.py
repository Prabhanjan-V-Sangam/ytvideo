from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NGINX_URL = "http://host.docker.internal:8080"

@app.route("/")
def index():
    # Fetch the directory listing from Nginx
    response = requests.get(NGINX_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract video links
    video_files = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href.endswith((".mp4", ".webm", ".mkv", ".avi", ".mov")):
            video_files.append(href)

    return render_template("index.html", video_files=video_files, nginx_url=NGINX_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
