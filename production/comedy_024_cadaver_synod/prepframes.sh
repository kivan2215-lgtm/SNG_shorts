set -eu
while [ ! -s court.mp4 ]; do sleep 2; done
while ! ffprobe -v error -show_entries format=duration -of csv=p=0 court.mp4 > /dev/null 2>&1; do sleep 1; done
mkdir -p court_frames
ffmpeg -y -v error -threads 1 -i court.mp4 -vf scale=720:1280 -q:v 2 -threads 1 court_frames/%04d.jpg
touch court_frames/complete
