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
        # Stream the video from Redis, part by part
        return Response(
            iter([video_data[i:i + CHUNK_SIZE] for i in range(0, len(video_data), CHUNK_SIZE)]),
            content_type="video/mp4"
        )

    # If the video is not cached, fetch from the source (video server)
    video_url = f"{VIDEO_SERVER_URL}{video_name}"
    response = requests.get(video_url, stream=True)

    if response.status_code == 200:
        # Read the video data in chunks and store it in Redis
        video_data = b"".join(response.iter_content(CHUNK_SIZE))
        
        # Cache the video in Redis (as a single block)
        redis_client.setex(f"video:{video_name}", 3600, video_data)  # Cache for 1 hour
        
        # Stream the video from the fetched data
        return Response(
            iter([video_data[i:i + CHUNK_SIZE] for i in range(0, len(video_data), CHUNK_SIZE)]),
            content_type="video/mp4"
        )
    
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

# Frontend: List and Watch Videos
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
    app.run(host="0.0.0.0", port=5000)
