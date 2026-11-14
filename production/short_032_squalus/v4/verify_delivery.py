from pathlib import Path
import requests,hashlib,json,time
P=Path(__file__).resolve().parents[1]
out=[]
for lang in ['ru','en']:
 f=P/lang/f'SNG_032_Squalus_{lang.upper()}_PREVIEW_V4.mp4'
 url='https://raw.githubusercontent.com/kivan2215-lgtm/SNG_shorts/main/'+f.name
 for attempt in range(4):
  r=requests.get(url,stream=True,timeout=60)
  if r.status_code==200:break
  r.close();time.sleep(3)
 r.raise_for_status();sha=hashlib.sha256();size=0
 for chunk in r.iter_content(1024*1024):sha.update(chunk);size+=len(chunk)
 local=hashlib.sha256(f.read_bytes()).hexdigest();assert sha.hexdigest()==local and size==f.stat().st_size
 row={'language':lang,'url':url,'http_status':r.status_code,'bytes':size,'content_type':r.headers.get('Content-Type'),'sha256':local,'download_matches_local':True};out.append(row)
 print(lang,'HTTP 200, full file hash verified',size,flush=True)
(P/'v4'/'delivery_verified.json').write_text(json.dumps(out,indent=2))
