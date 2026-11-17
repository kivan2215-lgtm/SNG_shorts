from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
from visuals import render,font
P=Path(__file__).parent
keys=['hold','outside','help','copilot','airport','alive','survived','ninety','difference','short','pressure','oversight','end']
for lang in ['ru','en']:
 scenes=json.loads((P/lang/'timeline.json').read_text());out=Image.new('RGB',(4*270,4*510),'#081824');d=ImageDraw.Draw(out);record=[]
 for i,k in enumerate(keys):
  s=next(x for x in scenes if x['visual']==k);t=(s['start']+s['end'])/2
  im=render(lang,k,.6,seconds=t-s['start']);f=P/'qc'/f'{lang}_{k}_raw.png';im.save(f);dest=P/'qc'/f'{lang}_{k}.jpg'
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-vf',f"setpts=PTS+{t}/TB,ass={P/lang/'subtitles.ass'}",'-frames:v','1',str(dest)],check=True);f.unlink()
  im=Image.open(dest);im.thumbnail((270,480));x=i%4*270;y=i//4*510;out.paste(im,(x,y+25));d.text((x+3,y+3),f'{t:.1f} {k}',font=font(14),fill='white');record.append({'shot':k,'time':t,'file':str(dest.name)})
 out.save(P/'qc'/f'{lang}_preflight.jpg');(P/'qc'/f'{lang}_preflight.json').write_text(json.dumps(record,indent=2))
