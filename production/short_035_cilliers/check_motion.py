from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,numpy as np
p=Path(__file__).parent;d=p/'frames/descent';meta=json.loads((d/'index.json').read_text());files=[d/f'{i:04d}.jpg' for i in range(61)];assert all(f.exists() for f in files);assert meta.get('processed')
a=np.asarray(Image.open(files[0])).astype(float);b=np.asarray(Image.open(files[-1])).astype(float);change=float(abs(a-b).mean());assert change>.3
sheet=Image.new('RGB',(5*216,414),'#071923');dr=ImageDraw.Draw(sheet)
for j,i in enumerate([0,15,30,45,60]):
 im=Image.open(files[i]);im.thumbnail((216,384));sheet.paste(im,(j*216,30));dr.text((j*216+5,5),f'frame {i} / {i/30:.1f}s',fill='white')
(p/'qc').mkdir(exist_ok=True);sheet.save(p/'qc/motion_review.jpg')
report={'frames':61,'fps':30,'duration':2,'source_size':[720,1280],'native_geometry_render':True,'optical_interpolation':False,'cache_region':meta['region'],'first_last_mean_abs_difference':change,'preview_not_approved':True,'manual_review':'pending'}
(p/'qc/motion_QC.json').write_text(json.dumps(report,indent=2))
