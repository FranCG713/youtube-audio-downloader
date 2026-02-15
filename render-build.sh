#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create bin directory if it doesn't exist
mkdir -p bin

# Download FFmpeg for Linux if it's not already there
if [ ! -f "bin/ffmpeg" ]; then
    echo "Downloading FFmpeg..."
    curl -L https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz
    tar -xf ffmpeg.tar.xz --strip-components=2 -C bin
    rm ffmpeg.tar.xz
fi

chmod +x bin/ffmpeg
chmod +x bin/ffprobe

echo "Build complete."
