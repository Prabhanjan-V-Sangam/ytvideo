import redis
import ffmpeg
import requests
from urllib.parse import quote
import io

CHUNK_SIZE = 1024 * 1024  # 1MB
REDIS_HOST = "192.168.1.8"  # Change to "redis" if using Docker Compose
REDIS_PORT = 6379

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username="default",
    password="user",
    decode_responses=False  # Store binary data
)

VIDEO_SERVER_URL = "http://192.168.1.8:8080/"  # Change if using another source


def download_mp4(video_key):
    url = f"{VIDEO_SERVER_URL}{quote(video_key)}"
    print(f"Downloading: {url}")

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {video_key}")
        return None

    return io.BytesIO(response.content)


def store_video_in_redis(video_key):
    """Convert MP4 to HLS and store in Redis as chunks and playlist."""
    video_stream = download_mp4(video_key)
    if not video_stream:
        return "Video not found"

    print(f"Converting {video_key} to HLS chunks")

    # FFmpeg HLS conversion
    process = (
        ffmpeg
        .input("pipe:")
        .output('pipe:', format='hls', hls_time=5, hls_list_size=0)
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )

    process.stdin.write(video_stream.read())
    process.stdin.close()

    playlist_data = b""
    ts_chunks = []
    while True:
        chunk = process.stdout.read(1024)
        if not chunk:
            break
        playlist_data += chunk

    process.wait()

    # For demonstration, save entire playlist as .m3u8 file content
    redis_client.set(f"video:{video_key}:playlist", playlist_data)

    # Example simulation of .ts chunks: you can use actual ffmpeg split output
    # Here we assume chunking is not in output, so we only simulate storing playlist
    redis_client.hset(f"video:{video_key}:m3u8", mapping={
        "filename": f"{video_key}.m3u8",
        "length": str(len(playlist_data)),
    })

    # Add to video list
    redis_client.lpush("video:list", video_key)

    # Track usage with ZSET
    redis_client.zincrby("video:cache:LRU", 1, video_key)

    print(f"Stored {video_key} HLS in Redis")
    return "Video stored in Redis"


if __name__ == "__main__":
    video_name = "sample.mp4"  # Change to your video name
    store_video_in_redis(video_name)
