from pathlib import Path
import hashlib,json,datetime
P=Path(__file__).parent
files={}
for f in P.rglob('*'):
 if not f.is_file() or any(x in f.parts for x in ['research','drafts','__pycache__','frames']):continue
 if f.suffix in ['.py','.txt','.md','.json','.ass','.srt','.png','.blend'] and f.name not in ['render_manifest.json','delivery_verified.json']:
  files[str(f.relative_to(P))]=hashlib.sha256(f.read_bytes()).hexdigest()
outputs=[]
for lang in ['ru','en']:
 f=P/lang/f'SNG_COMEDY_001_EMU_{lang.upper()}_PREVIEW_V5.mp4'
 if f.exists():outputs.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'render_manifest.json').write_text(json.dumps({'series':'SNG Comedy','episode':1,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'outputs':outputs,'status':'preview_pending_user_review','auditory_review':False},indent=2))
