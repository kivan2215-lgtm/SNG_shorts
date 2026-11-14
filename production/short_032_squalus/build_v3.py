"""Assemble revised 3-D visuals, preserving the approved timing/audio/captions."""
from pathlib import Path
import sys,json,subprocess,math,os
from PIL import Image,ImageDraw
from visuals_v3 import render,font

P=Path(__file__).parent
LANG=sys.argv[1] if len(sys.argv)>1 else 'ru'
L=P/LANG; OUT=L/'v3';OUT.mkdir(exist_ok=True)
shots=json.loads((L/'timeline.json').read_text())
duration=shots[-1]['end']
if not (L/'mix.wav').exists():
    subprocess.run([sys.executable,str(P/'build.py'),LANG,'--audio-only'],check=True)
sheet=Image.new('RGB',(1080,math.ceil(len(shots)/5)*424),'#081923')
d=ImageDraw.Draw(sheet)
for i,s in enumerate(shots):
    im=render(LANG,s['visual'],.7);im.save(OUT/f'frame_{i:02}_{s["visual"]}.jpg',quality=93)
    im.thumbnail((216,384));x=i%5*216;y=i//5*424;sheet.paste(im,(x,y+30))
    d.text((x+5,y+5),f'{s["start"]:.1f}s {s["visual"]}',font=font(13),fill='white')
sheet.save(OUT/'contact_sheet.jpg',quality=93)
if '--stills' in sys.argv:sys.exit(0)

suffix=os.environ.get('SNG_RENDER_SUFFIX','_V3')
output=L/f'SNG_032_Squalus_{LANG.upper()}_PREVIEW{suffix}.mp4'
args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-i',str(L/'mix.wav'),'-vf',f'ass={L/"subtitles.ass"}',
      '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3','-g','60','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(duration),'-movflags','+faststart',str(output)]
with (OUT/'render.log').open('w') as log:
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=log)
    try:
        for s in shots:
            count=round((s['end']-s['start'])*30)
            still=render(LANG,s['visual'],.5).tobytes() if s['visual'] in ['divers','construction','ships','bell_archive','honors','trapped'] else None
            for i in range(count):proc.stdin.write(still if still else render(LANG,s['visual'],i/max(1,count-1)).tobytes())
            print(LANG,s['visual'],s['end'],flush=True)
    finally:proc.stdin.close()
    code=proc.wait()
if code:raise RuntimeError(f'ffmpeg exit {code}')
print('READY',output,flush=True)
