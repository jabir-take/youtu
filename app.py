from flask import Flask, request, render_template
from pytube import YouTube #pip install pytube https://pypi.org/project/pytube/
from pathlib import Path #pip install pathlib https://pypi.org/project/pathlib/
import os
import re
 
app = Flask(__name__)
 
@app.route("/download", methods=["GET","POST"])
def downloadVideo():      
    mesage = ''
    errorType = 0
    if request.method == 'POST' and 'video_url' in request.form:
        youtubeUrl = request.form["video_url"]
        if(youtubeUrl):
            validateVideoUrl = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            validVideoUrl = re.match(validateVideoUrl, youtubeUrl)
            if validVideoUrl:
                url = YouTube(youtubeUrl)
                video = url.streams.get_highest_resolution()
                downloadFolder = str(os.path.join(Path.home(), "Downloads/Youtube_download"))
                video.download(downloadFolder)
                mesage = 'Video Downloaded Successfully!'
                errorType = 1
            else:
                mesage = 'Enter Valid YouTube Video URL!'
                errorType = 0
        else:
            mesage = 'Enter YouTube Video Url.'
            errorType = 0           
    return render_template('youtube.html', mesage = mesage, errorType = errorType) 
 
if __name__ == "__main__":
    app.run()