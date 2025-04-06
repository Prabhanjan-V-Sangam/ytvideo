import os
import redis
import requests
from urllib.parse import unquote
import tempfile

REDIS_HOST = "localhost"
REDIS_PORT = 6379
VIDEO_SERVER = "http://localhost:8080/"

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

CHUNK_SIZE = 1024 * 1024  # 1MB

def store_chunk(video_name, start_chunk):
    video_name = unquote(video_name)
    video_id = video_name.replace(" ", "_")
    video_url = VIDEO_SERVER + video_name

    headers = {'Range': f'bytes={start_chunk * CHUNK_SIZE}-{(start_chunk + 1) * CHUNK_SIZE - 1}'}
    r = requests.get(video_url, headers=headers, stream=True)

    if r.status_code not in [200, 206]:
        return "Failed to fetch chunk"

    chunk_data = r.content
    redis_key = f"video:{video_id}:chunk:{start_chunk}"
    redis_client.set(redis_key, chunk_data)
    redis_client.zadd("video:cache:LRU", {redis_key: 0})
    redis_client.rpush("video:list", video_id)

    return f"Stored chunk {start_chunk} of {video_id}"

if __name__ == "__main__":
    test_video = "You're Studying at an Oxford Library at Night _ Dark Academia Playlist.mp4"
    print(store_chunk(test_video, 0))
