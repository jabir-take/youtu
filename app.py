import time
from flask import Flask, render_template_string, request
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template_string(open("templates/index.html").read())
    except FileNotFoundError:
        return "Error: index.html not found!", 404

@app.route('/download', methods=['POST'])
def downloadVideo():
    url = request.form.get('url')
    if not url:
        return "Error: No URL provided", 400

    try:
        video = YouTube(url)
        stream = video.streams.get_highest_resolution()
        stream.download()  # Replace with actual download path and logic
        return f"Video downloaded successfully: {video.title}"
    except VideoUnavailable:
        return "Error: Video unavailable.", 404
    except Exception as e:
        if "429" in str(e):
            print("Rate limit exceeded, retrying...")
            time.sleep(10)  # Wait for 10 seconds before retrying
            return downloadVideo()  # Retry the download
        else:
            return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
