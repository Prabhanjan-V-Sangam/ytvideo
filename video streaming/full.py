from flask import Flask, request, jsonify
from video_storage import store_video  # Import the function from the first script

app = Flask(__name__)

@app.route("/store_video", methods=["POST"])
def store_video_route():
    data = request.json
    video_name = data.get("video_name")
    video_url = data.get("video_url")

    if not video_name or not video_url:
        return jsonify({"error": "Missing video name or video URL"}), 400

    store_video(video_name, video_url)
    return jsonify({"message": f"Video {video_name} is being stored in Redis."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
