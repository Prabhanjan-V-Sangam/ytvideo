from flask import Flask, Response, render_template, send_file
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=False)

VIDEO_NAME = "Mike_Mentzer_Bodybuilding_Edit_4_.mp4"

@app.route("/")
def index():
    return render_template("corn.html")

@app.route("/playlist.m3u8")
def playlist():
    meta_key = f"video:{VIDEO_NAME}:meta"
    total_chunks = int(r.hget(meta_key, "total_chunks"))
    
    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        "#EXT-X-TARGETDURATION:10",
        "#EXT-X-MEDIA-SEQUENCE:0"
    ]
    
    for i in range(total_chunks):
        lines.append("#EXTINF:10.0,")
        lines.append(f"/chunk/{i}.ts")
    
    lines.append("#EXT-X-ENDLIST")
    
    return Response("\n".join(lines), mimetype="application/vnd.apple.mpegurl")

@app.route("/chunk/<int:index>.ts")
def chunk(index):
    key = f"video:{VIDEO_NAME}:chunks"
    chunk_data = r.hget(key, str(index))
    if chunk_data:
        return Response(chunk_data, mimetype="video/MP2T")
    return "Chunk not found", 404
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)