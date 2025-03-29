import redis
import requests

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk
REDIS_HOST = "localhost"
REDIS_PORT = 6379
#redis_url = "redis://default:userp@localhost:6379/0"



def store_video_in_redis(video_name):
    #redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    #redis_client = redis.StrictRedis(redis_url,decoder_responses=False)
    redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=0, 
    username="default",  # Add username
    password="user",    # Add password
    decode_responses=False  # Set to False for binary data
)
    url = f"http://localhost:8080/what%20if%20you%20weren%27t%20afraid_.mp4"
    
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Failed to download {video_name}")
        return

    chunk_index = 0
    for chunk in response.iter_content(CHUNK_SIZE):
        redis_client.set(f"{video_name}:chunk:{chunk_index}", chunk)
        chunk_index += 1

    redis_client.set(f"{video_name}:total_chunks", chunk_index)
    print(f"Stored {video_name} in Redis ({chunk_index} chunks)")

if __name__ == "__main__":
    video_name = "sample.mp4"  # Change this to your video filename
    store_video_in_redis(video_name)
