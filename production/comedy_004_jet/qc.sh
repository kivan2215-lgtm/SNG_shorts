set -eu
f=SNG_COMEDY_004_JET_$1.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration -of json "$f" > "$1-probe.json"
ffmpeg -v error -i "$f" -f null -
ffmpeg -loglevel error -y -i "$f" -vf 'fps=1/3,scale=144:256,tile=6x4' -frames:v 1 "$1-sheet.jpg"
