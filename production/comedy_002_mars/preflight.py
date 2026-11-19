from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
from visuals import render,font
P=Path(__file__).parent;(P/'qc').mkdir(exist_ok=True)
for lang in ['ru','en']:
 scenes=json.loads((P/lang/'timeline.json').read_text());keys=['hook','report','units_a','units_b','transfer','factor','drift','lowpass','checks','door','question'];out=Image.new('RGB',(1080,2040),'#102029')
 for i,k in enumerate(keys):
  s=next(x for x in scenes if x['visual']==k);t=(s['start']+s['end'])/2;f=P/'qc'/f'{lang}_{k}_raw.png';dest=P/'qc'/f'{lang}_{k}.jpg';render(lang,k,.5,seconds=t-s['start']).save(f)
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-vf',f"setpts=PTS+{t}/TB,ass={P/lang/'subtitles.ass'}",'-frames:v','1',str(dest)],check=True);f.unlink();im=Image.open(dest);im.thumbnail((270,480));out.paste(im,(i%4*270,i//4*510))
 out.save(P/'qc'/f'{lang}_preflight.jpg')
