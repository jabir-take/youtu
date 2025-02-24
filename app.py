import time
from flask import Flask, render_template, request, Response
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

app = Flask(__name__)

# Maximum number of retries for rate limit issues
MAX_RETRIES = 3

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except FileNotFoundError:
        return "Error: index.html not found!", 404

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return "Error: No URL provided", 400

    retries = 0

    while retries < MAX_RETRIES:
        try:
            video = YouTube(url)
            stream = video.streams.get_highest_resolution()

            # Function to stream video directly to the user
            def generate():
                for chunk in stream.stream_to_buffer():
                    yield chunk

            return Response(generate(), 
                            mimetype='video/mp4',
                            content_type='video/mp4', 
                            headers={'Content-Disposition': f'attachment; filename={video.title}.mp4'})

        except VideoUnavailable:
            return "Error: Video unavailable.", 404
        except Exception as e:
            if "429" in str(e):  # Rate limit exceeded error
                retries += 1
                print(f"Rate limit exceeded, retrying... ({retries}/{MAX_RETRIES})")
                time.sleep(10)  # Wait for 10 seconds before retrying
            else:
                return f"Error: {str(e)}", 500

    return "Error: Max retries exceeded. Could not download the video.", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
