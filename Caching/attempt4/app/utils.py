# app/utils.py
import redis
import requests
from urllib.parse import unquote

REDIS_HOST = "redis"
REDIS_PORT = 6379
CHUNK_SIZE = 1024 * 1024  # 1 MB
VIDEO_SERVER = "http://192.168.1.8:8080/"  # External video server

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

def fetch_and_store_chunk(video_name, chunk_id):
    video_name = unquote(video_name)
    video_id = video_name.replace(" ", "_")
    start_byte = chunk_id * CHUNK_SIZE
    end_byte = start_byte + CHUNK_SIZE - 1
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}

    try:
        response = requests.get(VIDEO_SERVER + video_name, headers=headers, stream=True)
        if response.status_code not in [200, 206]:
            return f"Failed to fetch chunk {chunk_id}"

        data = response.content
        redis_key = f"video:{video_id}:chunk:{chunk_id}"
        redis_client.set(redis_key, data)
        redis_client.zadd("video:cache:LRU", {redis_key: 0})
        redis_client.rpush(f"video:list:{video_id}", redis_key)

        return f"Stored chunk {chunk_id} of {video_id}"
    except Exception as e:
        return f"Error: {str(e)}"
