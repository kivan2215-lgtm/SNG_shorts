from pathlib import Path
import json
from visuals import ART,PHOTOS
P=Path(__file__).parent;out={'series':'SNG Comedy','episode':2,'status':'preview_pending_user_review','languages':{}}
for l in ['ru','en']:
 words=json.loads((P/l/'words.json').read_text());shots=json.loads((P/l/'timeline.json').read_text())
 for s in shots:
  k=s['visual'];s['narration']=' '.join(w['text'] for w in words if s['start']-.03<=w['start']<s['end']-.03);s['camera']='fixed';s['heading']=None;s['manual_review']='pending'
  if k in ART:s['asset']=f'scenes{ART[k][0]}.png:panel{ART[k][1]}';s['provenance']='original editorial illustration, not archival footage'
  elif k in PHOTOS:s['asset']=PHOTOS[k];s['provenance']='actual NASA photograph; assets.json'
  elif k in ['report','report2']:s['asset']='report_root.png';s['provenance']='official report page16 excerpt'
  else:s['asset']='original Blender model plus explanatory overlays';s['provenance']='schematic, not exact geometry or historical software interface'
  s['purpose']={'units_a':'Identify output impulse units at source program','units_b':'Identify different expected units at receiving program','transfer':'Show unchanged number transmitted without required unit conversion','factor':'Show correct conversion factor, not a whole-orbit error factor','drift':'Distinguish calculated versus lower actual pass; not to scale','lowpass':'Move spacecraft along low arc; no explosion claim','lost':'State mission loss without inventing final physical fate','checks':'Show error passing data/check/model stages; not actual audit log','door':'Make narrator VIP metaphor visible','launch':'Show actual launch on exact date','journey':'Launch-pad context plus elapsed cruise label, not flight footage'}.get(k,'Illustrate the current recorded phrase, preserve factual versus comic context')
 out['languages'][l]=shots
(P/'shot_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
