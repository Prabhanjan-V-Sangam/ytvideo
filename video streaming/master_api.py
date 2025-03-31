from flask import Flask, request, Response, jsonify
import redis
import requests

app = Flask(__name__)

# Redis Configuration
CHUNK_SIZE = 1024 * 1024  # 1MB per chunk
REDIS_HOST = "redis"  # Use container name in Docker network
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
    decode_responses=False  # Storing binary video chunks
)

VIDEO_SERVER_URL = "http://host.docker.internal:8080/"

@app.route("/video/<video_name>", methods=["GET"])
def get_video(video_name):
    cached_video = redis_client.get(f"video:{video_name}")

    if cached_video:
        print(f"Serving {video_name} from Redis cache...")
        return Response(cached_video, content_type="video/mp4")

    # If not found, fetch from source
    video_url = f"{VIDEO_SERVER_URL}{video_name}"
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        video_data = b"".join(response.iter_content(CHUNK_SIZE))

        # Cache the video in Redis
        redis_client.setex(f"video:{video_name}", 3600, video_data)  # Expires in 1 hour

        return Response(video_data, content_type="video/mp4")

    return jsonify({"error": "Video not found"}), 404

@app.route("/videos", methods=["GET"])
def list_videos():
    keys = redis_client.keys("video:*")
    videos = [key.decode("utf-8").split(":")[1] for key in keys]
    return jsonify({"cached_videos": videos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

''' initial attempt 1
from flask import Flask, request, Response, jsonify
import redis
import requests

app = Flask(__name__)

# Connect to Redis
redis_client = redis.Redis(host="redis-service", port=6379, decode_responses=True)

VIDEO_SERVER_URL = "http://host.docker.internal:8080/"

@app.route("/video/<video_name>", methods=["GET"])
def get_video(video_name):
    # Check if video is cached
    cached_video_url = redis_client.hget(f"video:{video_name}", "url")

    if cached_video_url:
        print(f"Serving {video_name} from Redis cache...")
        return Response(requests.get(cached_video_url).content, content_type="video/mp4")

    # If not found, fetch from source
    video_url = f"{VIDEO_SERVER_URL}{video_name}"
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        # Cache the video URL
        redis_client.hset(f"video:{video_name}", mapping={"url": video_url, "status": "cached"})
        redis_client.expire(f"video:{video_name}", 3600)  # Cache for 1 hour

        return Response(response.content, content_type="video/mp4")
    
    return jsonify({"error": "Video not found"}), 404

@app.route("/videos", methods=["GET"])
def list_videos():
    # Fetch cached video names
    keys = redis_client.keys("video:*")
    videos = [key.split(":")[1] for key in keys]
    return jsonify({"cached_videos": videos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''