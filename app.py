import time
import logging
from flask import Flask, render_template, request, Response
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, StreamError

app = Flask(__name__)

# Enable logging to track retries and errors
logging.basicConfig(level=logging.DEBUG)

# Maximum number of retries for rate limit or transient errors
MAX_RETRIES = 3
RETRY_DELAY = 30  # Time to wait (in seconds) between retries

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
            # Initialize the YouTube object
            video = YouTube(url)
            stream = video.streams.get_highest_resolution()

            # Stream video directly to the user (allow download)
            def generate():
                for chunk in stream.stream_to_buffer():
                    yield chunk

            return Response(generate(), 
                            mimetype='video/mp4',
                            content_type='video/mp4', 
                            headers={'Content-Disposition': f'attachment; filename={video.title}.mp4'})

        except VideoUnavailable:
            # Log if the video is unavailable (e.g., private or geo-restricted)
            logging.error(f"Video unavailable: {url}")
            return "Error: Video unavailable (may be private or geo-restricted).", 404
        except StreamError:
            # Log if there's an issue with stream availability
            logging.error(f"Stream unavailable: {url}")
            return "Error: Stream not available for this video.", 404
        except Exception as e:
            retries += 1
            logging.error(f"Attempt {retries}/{MAX_RETRIES} failed with error: {str(e)}")
            if "429" in str(e):  # Handle rate-limiting error from YouTube
                logging.warning(f"Rate limit exceeded. Retrying after {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                logging.error(f"Unexpected error occurred: {str(e)}")
                return f"Error: {str(e)}", 500

    # After all retries, if failed
    logging.error("Max retries exceeded, could not download the video.")
    return "Error: Max retries exceeded. Could not download the video.", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
