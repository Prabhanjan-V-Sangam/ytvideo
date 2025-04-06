import redis
import requests
from bs4 import BeautifulSoup

VIDEO_SERVER_URL = "http://192.168.1.8:8080/"
REDIS_HOST = "192.168.1.8"
REDIS_PORT = 6379

redis_client = redis.StrictRedis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=0, 
    username="default", 
    password="user", 
    decode_responses=True
)

def fetch_video_links():
    try:
        response = requests.get(VIDEO_SERVER_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        videos = [link.get("href") for link in soup.find_all("a") if link.get("href").endswith(".mp4")]
        if videos:
            redis_client.delete("video:list")
            redis_client.rpush("video:list", *videos)
            print(f"Stored {len(videos)} videos.")
        else:
            print("No videos found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_video_links()
