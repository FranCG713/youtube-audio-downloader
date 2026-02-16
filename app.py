import os
import time
import glob
from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Configure upload/download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Cloud Specific: Get FFmpeg path from environment variable or local folder
# On Render, we'll set FFMPEG_PATH to point to our downloaded binary
FFMPEG_EXE = os.environ.get('FFMPEG_PATH', os.path.join(os.getcwd(), 'bin', 'ffmpeg'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Generate a unique filename prefix to avoid collisions
        timestamp = int(time.time())
        
        # Advanced options to bypass data-center blocks (Render)
        ydl_opts = {
            'format': 'bestaudio/best', 
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s-%(id)s.%(ext)s',
            'restrictfilenames': True,
            'ffmpeg_location': FFMPEG_EXE,
            'quiet': False, 
            'no_warnings': False,
            'nocheckcertificate': True,
            'cachedir': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'web'],
                    'skip': ['dash', 'hls']
                }
            }
        }

        # Check for cookies file and log it
        cookies_path = os.path.join(os.getcwd(), 'cookies.txt')
        if os.path.exists(cookies_path):
            print(f"DEBUG: Using cookies.txt at {cookies_path}")
            ydl_opts['cookiefile'] = cookies_path
        else:
            print("DEBUG: cookies.txt NOT found in the app directory")

        info_dict = None
        with YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the filename
            info_dict = ydl.extract_info(video_url, download=True)
            
            if not info_dict:
                 return jsonify({'error': 'No se pudo obtener la información del video. ¿Es el enlace correcto o privado?'}), 500
            
            # Prepare the expected filename
            video_id = info_dict.get('id', None)
            video_title = info_dict.get('title', None)
            
            # Search for the file in the download folder matching the ID
            search_pattern = f"{DOWNLOAD_FOLDER}/*{video_id}.mp3"
            files = glob.glob(search_pattern)
            
            if not files:
                 return jsonify({'error': 'Conversion failed, file not found'}), 500
            
            mp3_file = files[0]
            
            return jsonify({
                'success': True,
                'download_url': f'/download_file?file={os.path.basename(mp3_file)}',
                'title': video_title,
                'thumbnail': info_dict.get('thumbnail')
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_file')
def download_file():
    filename = request.args.get('file')
    if not filename:
        return "Filename missing", 400
    
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found", 404

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    # For local testing of the cloud version
    app.run(debug=True, host='0.0.0.0', port=5000)
