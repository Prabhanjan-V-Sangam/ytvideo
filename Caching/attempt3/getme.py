import redis
import requests
from bs4 import BeautifulSoup

# Redis Configuration
REDIS_HOST = "192.168.1.8"
REDIS_PORT = 6379
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    username="default",
    password="user",
    decode_responses=True  # Store as readable text
)

VIDEO_SERVER_URL = "http://192.168.1.8:8080/"  # Change this if needed

def fetch_video_links():
    """Fetch all video links from the local video server and store them in Redis."""
    try:
        response = requests.get(VIDEO_SERVER_URL)
        if response.status_code != 200:
            print(f"Error: Unable to fetch videos from {VIDEO_SERVER_URL} (Status: {response.status_code})")
            return
        
        # Parse HTML response to extract links
        soup = BeautifulSoup(response.text, "html.parser")
        video_links = []

        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".mp4"):  # Only store .mp4 files
                video_links.append(href)

        if not video_links:
            print("No videos found on the server.")
            return

        # Store in Redis List (overwrite existing)
        redis_client.delete("video:list")  # Clear old entries
        redis_client.rpush("video:list", *video_links)
        print(f"Stored {len(video_links)} videos in Redis.")

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    fetch_video_links()
