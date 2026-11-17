from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
P=Path(__file__).parent
results=[]
for k,n in [('window',37),('bolts',61)]:
 p=P/'frames'/k;missing=[i for i in range(n) if not (p/f'{i:04}.jpg').exists()]
 if missing:raise RuntimeError((k,missing))
 ids=sorted(set([0,(n-1)//6,(n-1)//3,(n-1)//2,2*(n-1)//3,5*(n-1)//6,n-1]));sheet=Image.new('RGB',(4*270,2*510),'#091824');d=ImageDraw.Draw(sheet);changes=[];prev=None
 for j,i in enumerate(ids):
  im=Image.open(p/f'{i:04}.jpg').convert('RGB');a=np.asarray(im,dtype=np.int16)
  if prev is not None:changes.append(float(np.abs(a-prev).mean()))
  prev=a;im.thumbnail((270,480));x=j%4*270;y=j//4*510;sheet.paste(im,(x,y+25));d.text((x+5,y+4),f'{k} frame{i}',fill='white')
 sheet.save(P/'qc'/f'{k}_motion.jpg');results.append({'kind':k,'frames':n,'native_fps':30,'no_optical_interpolation':True,'sampled_ids':ids,'sample_pixel_changes':changes,'manual_review':'pending'})
(P/'qc/motion_QC.json').write_text(json.dumps(results,indent=2));print(results)
