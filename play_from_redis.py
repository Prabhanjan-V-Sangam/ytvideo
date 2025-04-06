from flask import Flask, Response, render_template, request
import redis
import urllib.parse

app = Flask(__name__)

# Redis setup
redis_client = redis.StrictRedis(
    host="192.168.1.8",
    port=6379,
    db=0,
    username="default",
    password="user",
    decode_responses=False  # Binary mode for video chunks
)


'''
# Util: get original name from metadata
def get_original_name(slug_name):
    meta_key = f"video:{slug_name}:meta"
    original = redis_client.hget(meta_key, "original_name")
    if original:
        return original.decode()
    return slug_name

@app.route("/")
def list_videos():
    keys = redis_client.keys("video:*:chunks")
    videos = []

    for key in keys:
        slug = key.decode().split("video:")[1].rsplit(":chunks", 1)[0]
        original_name = get_original_name(slug)
        videos.append({"slug": slug, "original": original_name})

    return render_template("videos.html", videos=videos)

@app.route("/watch/<video_slug>")
def watch(video_slug):
    original_name = get_original_name(video_slug)
    return render_template("watch.html", video_name=video_slug, display_name=original_name)

@app.route("/stream/<video_slug>")
def stream(video_slug):
    chunk_hash = f"video:{video_slug}:chunks"

    # Get sorted chunk indices
    chunk_indices = sorted(
        [int(k.decode()) for k in redis_client.hkeys(chunk_hash)]
    )

    def generate():
        for index in chunk_indices:
            chunk = redis_client.hget(chunk_hash, str(index))
            if chunk:
                yield chunk

    return Response(generate(), mimetype="video/mp4")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
'''