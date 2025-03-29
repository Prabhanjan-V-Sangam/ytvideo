from flask import Flask, Response, render_template
import redis

app = Flask(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
VIDEO_NAME = "sample.mp4"

#redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=0, 
    username="default",  # Add username
    password="user",    # Add password
    decode_responses=False  # Set to False for binary data
)

def stream_video():
    total_chunks = int(redis_client.get(f"{VIDEO_NAME}:total_chunks") or 0)
    if total_chunks == 0:
        return Response("Video not found", status=404)

    def generate():
        for chunk_index in range(total_chunks):
            chunk_data = redis_client.get(f"{VIDEO_NAME}:chunk:{chunk_index}")
            if chunk_data:
                yield chunk_data

    return Response(generate(), content_type="video/mp4")

@app.route("/")
def index():
    return render_template("index.html", video_name=VIDEO_NAME)

@app.route("/video")
def video():
    return stream_video()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
