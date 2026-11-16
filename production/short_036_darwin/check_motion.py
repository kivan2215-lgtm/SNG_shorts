from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
p=Path(__file__).parent;d=p/'frames/passage';meta=json.loads((d/'index.json').read_text());files=[d/f'{i:04d}.jpg' for i in range(91)];assert all(f.exists() for f in files);assert meta.get('processed')
a=np.asarray(Image.open(files[0])).astype(float);b=np.asarray(Image.open(files[-1])).astype(float);change=float(abs(a-b).mean());assert change>.1
sheet=Image.new('RGB',(4*270,2*510),'#071923');dr=ImageDraw.Draw(sheet)
for j,i in enumerate([0,12,24,36,48,60,75,90]):
 im=Image.open(files[i]);im.thumbnail((270,480));x=j%4*270;y=j//4*510;sheet.paste(im,(x,y+30));dr.text((x+5,y+5),f'frame {i} / {i/30:.2f}s',fill='white')
(p/'qc').mkdir(exist_ok=True);sheet.save(p/'qc/motion_review.jpg')
report={'frames':91,'fps':30,'duration':3,'source_size':[720,1280],'native_geometry_render':True,'optical_interpolation':False,'cache_region':meta['region'],'first_last_mean_abs_difference':change,'preview_not_approved':True,'manual_review':'pending'}
(p/'qc/motion_QC.json').write_text(json.dumps(report,indent=2))
