from pathlib import Path
import requests,hashlib,json,concurrent.futures,datetime,time
P=Path(__file__).parent
D=Path('/workspace/sng-publish/production/comedy_001_emu/v2')
def check(lang):
 name=f'SNG_COMEDY_001_EMU_{lang.upper()}_PREVIEW_V2.mp4';url='https://raw.githubusercontent.com/kivan2215-lgtm/SNG_shorts/main/'+name;expected=hashlib.sha256((P/lang/name).read_bytes()).hexdigest()
 for attempt in range(5):
  r=requests.get(url,timeout=120)
  if r.status_code==200 and hashlib.sha256(r.content).hexdigest()==expected:break
  if attempt==4:raise RuntimeError(f'Download verification failed: {name}, status {r.status_code}')
  time.sleep(5)
 return {'language':lang,'url':url,'sha256':expected,'bytes':len(r.content),'full_download_verified':True,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:checks=list(pool.map(check,['ru','en']))
for folder in [P,D]:
 if folder.exists():(folder/'delivery_verified.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
