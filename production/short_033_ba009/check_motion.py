from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).parent
out=[]
for kind in ['deposit','clear','glide']:
 d=P/'frames'/kind;m=json.loads((d/'index.json').read_text());assert m['count']==61
 diffs=[];prev=None
 for i in range(61):
  f=d/f'{i:04d}.jpg';a=np.asarray(Image.open(f).convert('RGB'),dtype='float32');assert a.shape==(1280,720,3)
  if prev is not None:diffs.append(float(np.mean(np.abs(a-prev))))
  prev=a
 sheet=Image.new('RGB',(5*216,384))
 for j,i in enumerate([0,15,30,45,60]):sheet.paste(Image.open(d/f'{i:04d}.jpg').resize((216,384)),(j*216,0))
 sheet.save(P/'tests'/f'{kind}_motion.jpg')
 out.append({'kind':kind,'frames':61,'fps':30,'native_action_seconds':2,'mean_frame_difference':sum(diffs)/60,'max_frame_difference':max(diffs),'frame_differences':diffs,'index_sha256':hashlib.sha256((d/'index.json').read_bytes()).hexdigest(),'review':'pending'})
(P/'motion_QC.json').write_text(json.dumps(out,indent=2))
