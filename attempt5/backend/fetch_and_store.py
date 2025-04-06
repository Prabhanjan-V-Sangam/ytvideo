import redis
import os
import subprocess
import requests

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD
)

NGINX_VIDEO_URL = "http://192.168.1.8:8081/videos/"

def store_video_in_redis(video_name):
    video_url = f"{NGINX_VIDEO_URL}{video_name}"
    video_file = f"/tmp/{video_name}"
    folder_name = f"/tmp/hls_{video_name}"
    playlist_path = os.path.join(folder_name, "playlist.m3u8")

    # Skip if already processed
    if redis_client.get(f"video:{video_name}:playlist"):
        print(f"[i] Video {video_name} already in Redis.")
        return

    try:
        # Download the video file
        print(f"[*] Downloading: {video_url}")
        r = requests.get(video_url, stream=True)
        with open(video_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        # Convert to HLS
        print("[*] Converting to HLS...")
        os.makedirs(folder_name, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-i", video_file,
            "-c:v", "libx264", "-c:a", "aac",
            "-f", "hls", "-hls_time", "10", "-hls_list_size", "0",
            "-hls_segment_filename", f"{folder_name}/chunk_%03d.ts",
            playlist_path
        ], check=True)

        # Store in Redis
        print("[*] Storing in Redis...")
        chunk_key = f"video:{video_name}:chunks"
        playlist_key = f"video:{video_name}:playlist"

        chunks = sorted(f for f in os.listdir(folder_name) if f.endswith(".ts"))
        for i, chunk in enumerate(chunks):
            with open(os.path.join(folder_name, chunk), 'rb') as f:
                redis_client.hset(chunk_key, str(i), f.read())
        with open(playlist_path, "r") as f:
            redis_client.set(playlist_key, f.read())

        print(f"[✓] Stored {len(chunks)} chunks and playlist for {video_name}.")

        # Cleanup
        os.remove(video_file)

    except Exception as e:
        print(f"[x] Failed to process {video_name}: {e}")
