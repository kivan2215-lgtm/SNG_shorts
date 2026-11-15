from pathlib import Path
import requests,json
from bs4 import BeautifulSoup
P=Path(__file__).parent;H={'User-Agent':'SNGDocumentaryResearch/1.0 (source verification)'}
items=[('plane','BA_747-200_G-BDXH_at_LHR_(16748337441).jpg','Gordon Bevan / G B_NZ','CC BY-SA 2.0','1982-01-23'),('blades','British-Airways-Flight-9_turbine_and_compressor_blades.JPG','Nova13','CC BY-SA 3.0','2008-07-04'),('volcano','Galunggung.jpg','R. Hadian / USGS, via NOAA','Public domain (US government)','1982-12-03')]
out=[]
for key,title,author,license,date in items:
 u='https://commons.wikimedia.org/wiki/File:'+title;r=requests.get(u,headers=H,timeout=40);r.raise_for_status();s=BeautifulSoup(r.text,'html.parser');(P/'research'/f'{key}_commons.html').write_text(r.text);(P/'research'/f'{key}_commons.txt').write_text(s.get_text(' ',strip=True));a=s.select_one('.fullImageLink a');url=a['href'];rr=requests.get(url,headers=H,timeout=40);rr.raise_for_status();f=P/'assets'/f'{key}.jpg';f.write_bytes(rr.content)
 from PIL import Image
 im=Image.open(f);out.append(dict(key=key,page=u,url=url,author=author,license=license,capture_date=date,size=im.size,changes='contained scaling in video, no invented detail'))
 print(key,im.size,s.get_text(' ',strip=True)[1500:6500] if key=='volcano' else license,flush=True)
(P/'assets.json').write_text(json.dumps(out,indent=2))
