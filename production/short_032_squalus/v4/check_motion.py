"""Catch missing frames and abrupt intra-shot picture jumps before assembly."""
from pathlib import Path
from PIL import Image
import numpy as np,json
P=Path(__file__).parent;reports=[]
for d in sorted((P/'frames').iterdir()):
 m=json.loads((d/'index.json').read_text());prev=None;diffs=[]
 for i in range(m['count']):
  a=np.asarray(Image.open(d/f'{i:04d}.jpg').convert('RGB').resize((180,320)),dtype=np.int16)
  if prev is not None:diffs.append(float(np.mean(abs(a-prev))))
  prev=a
 med=float(np.median(diffs));peak=max(diffs);threshold=max(10,8*med)
 row={'scene':d.name,'frames':m['count'],'native_fps':m['render_fps'],'median_frame_change':med,'peak_frame_change':peak,'abrupt_change_flag':peak>threshold,'region':m.get('region')};reports.append(row)
print(json.dumps(reports,indent=2));(P/'motion_QC.json').write_text(json.dumps(reports,indent=2))
assert not any(r['abrupt_change_flag'] for r in reports), 'Inspect flagged scene before continuing'
