import redis
from flask import Flask, Response
import io

app = Flask(__name__)

# Redis client setup (Make sure to use your own connection details)
r = redis.StrictRedis(
    host="192.168.1.8",  # Your Redis server address
    port=6379,
    db=0,
    username="default",
    password="user",
    decode_responses=False  # to handle binary data (e.g., video)
)

# Video file and chunks hash key (adjust with the correct video name)
video_hash_key = 'video:Mike_Mentzer_Bodybuilding_Edit_4_.mp4:chunks'

# Function to get and yield chunks in correct order from Redis
def get_video_chunks():
    # Get all the chunk keys from the Redis hash
    chunk_keys = r.hkeys(video_hash_key)

    # Sort the keys numerically (if chunk keys are numeric, adjust accordingly)
    sorted_chunk_keys = sorted(chunk_keys, key=lambda x: int(x))

    # Iterate through sorted chunk keys and yield each chunk
    for chunk_key in sorted_chunk_keys:
        # Get the chunk data from Redis
        chunk_data = r.hget(video_hash_key, chunk_key)
        
        # Ensure chunk_data is not None or empty before yielding
        if chunk_data:
            print(f"Serving chunk: {chunk_key}")  # Debugging
            yield chunk_data  # Streaming each chunk
        else:
            print(f"Warning: Chunk {chunk_key} is empty or not found.")  # Debugging

@app.route('/video')
def stream_video():
    # Streaming the video chunks directly to the browser
    return Response(get_video_chunks(), content_type='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
