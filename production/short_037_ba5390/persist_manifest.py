from pathlib import Path
import hashlib,json
P=Path(__file__).parent
paths=list(P.glob('*.py'))+list(P.glob('*.md'))+list(P.glob('*.txt'))+list((P/'assets').glob('*'))
for lang in ['ru','en']:
 paths+=list((P/lang).glob('*.txt'))+list((P/lang).glob('*.json'))
files={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths if f.is_file()}
outputs={}
for lang in ['ru','en']:
 f=P/lang/f'SNG_037_BA5390_{lang.upper()}_PREVIEW.mp4'
 if f.exists():outputs[f.name]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'render_manifest.json').write_text(json.dumps({'episode':37,'status':'preview_pending_user_review','source_model_resolution':[720,1280],'output':[1080,1920,30],'files':files,'outputs':outputs,'auditory_review':False},indent=2))
