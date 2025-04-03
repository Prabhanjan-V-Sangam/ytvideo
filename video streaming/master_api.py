'''
import redis
import requests
from flask import Flask, request, Response, jsonify
from urllib.parse import unquote  # Import unquote to decode the URL

app = Flask(__name__)

# Redis Configuration
CHUNK_SIZE = 1024 * 1024  # 1MB per chunk
REDIS_HOST = "redis"  # Redis container hostname
REDIS_PORT = 6379
REDIS_USERNAME = "default"
REDIS_PASSWORD = "user"

# Redis Connection
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=False  # Store binary video chunks
)

VIDEO_SERVER_URL = "http://localhost:8080/"  # URL of the video server

@app.route("/watch/<video_name>", methods=["GET"])
def watch_video(video_name):
    # Decode the video name to handle URL encoding correctly
    video_name = unquote(video_name)  # Decode the video name to handle double encoding

    print(f"Serving video: {video_name}")

    # Check if the video is cached in Redis
    video_data = redis_client.get(f"video:{video_name}")
    
    if video_data:
        print(f"Serving {video_name} from Redis cache...")
        return Response(video_data, content_type="video/mp4")

    # If the video is not cached, fetch from the source (video server)
    video_url = f"{VIDEO_SERVER_URL}{video_name}"
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        # Read the video data in chunks and store it in Redis
        video_data = b"".join(response.iter_content(CHUNK_SIZE))
        
        # Cache the video in Redis (as a single block)
        redis_client.setex(f"video:{video_name}", 3600, video_data)  # Cache for 1 hour
        
        return Response(video_data, content_type="video/mp4")
    
    return jsonify({"error": "Video not found"}), 404

@app.route("/cache_video/<video_name>", methods=["POST"])
def cache_video(video_name):
    # Decode the video name to handle URL encoding correctly
    video_name = unquote(video_name)  # Decode the video name to handle double encoding

    # Fetch the video from the server and store it in Redis
    video_url = f"{VIDEO_SERVER_URL}{video_name}"
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        # Store the video in Redis in chunks
        video_data = b"".join(response.iter_content(CHUNK_SIZE))
        
        # Cache the video in Redis
        redis_client.setex(f"video:{video_name}", 3600, video_data)  # Cache for 1 hour
        
        return jsonify({"message": f"Video {video_name} successfully cached in Redis."}), 200

    return jsonify({"error": f"Failed to download {video_name} from the server."}), 404

@app.route("/videos", methods=["GET"])
def list_videos():
    # List all videos that are cached in Redis
    keys = redis_client.keys("video:*")
    videos = [key.decode("utf-8").split(":")[1] for key in keys]
    return jsonify({"cached_videos": videos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''

from flask import Flask, Response, render_template, jsonify
import redis
import requests

app = Flask(__name__)

# Redis connection details
REDIS_HOST = "localhost"
REDIS_PORT = 6379
VIDEO_NAME = "sample.mp4"
VIDEO_URL = "http://localhost:8080/sample.mp4"  # Change this URL to your video source

# Redis client
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username="default",  # Add username
    password="user",  # Add password
    decode_responses=False  # Set to False for binary data
)

# Function to stream the video from Redis
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

# Route to store the video in Redis
@app.route("/store_video", methods=["POST"])
def store_video():
    # Trigger the first script to store the video in Redis
    response = requests.post("http://localhost:5001/store_video", json={"video_name": VIDEO_NAME, "video_url": VIDEO_URL})

    if response.status_code == 200:
        return jsonify({"message": f"Video {VIDEO_NAME} stored in Redis successfully!"}), 200
    else:
        return jsonify({"error": "Failed to store video"}), 500

# Route to view the video
@app.route("/video")
def video():
    return stream_video()

# Frontend route to trigger the video storage
@app.route("/")
def index():
    return render_template("index.html", video_name=VIDEO_NAME)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
