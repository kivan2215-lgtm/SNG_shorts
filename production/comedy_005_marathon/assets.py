from pathlib import Path
from bs4 import BeautifulSoup as B
import json,subprocess as sp,urllib.parse,concurrent.futures
from io import BytesIO
from PIL import Image
wanted={'Marathon_Hicks':'hicks','1904_Olympics-_Runners':'start','First_runners':'track','Fred_Lorz_Cartoon':'cartoon','1904_Olympics-_Thomas':'rest','Frederick_Lorz_1904':'lorz'}
imgs={}
for pg in ['race','lorz']:
 for im in B(Path(pg+'.html').read_text(),'html.parser').select('img'):
  src=im.get('src','').split('?')[0]
  for pref,key in wanted.items():
   if '/'+pref in src:imgs[key]=src
def fetch(it):
 k,src=it
 uri='https:'+src.replace('thumb.wikimedia','upload.wikimedia').replace('/thumb/','/').rsplit('/',1)[0]; name=urllib.parse.unquote(uri.rsplit('/',1)[1]);img=Image.open(BytesIO(sp.check_output(['curl','-fsSL','--retry','2','--max-time','55',uri])));img.thumbnail((1900,2000));img.convert('RGB').save(k+'.jpg',quality=94)
 doc=json.loads(sp.check_output(['curl','-fsSLG','--max-time','35','--data-urlencode','titles=File:'+name,'--data','action=query&prop=imageinfo&iiprop=extmetadata&format=json','https://commons.wikimedia.org/w/api.php']))
 meta=next(iter(doc['query']['pages'].values()))['imageinfo'][0]['extmetadata']
 def txt(k):return B(meta.get(k,{}).get('value',''),'html.parser').get_text(' ',strip=True)
 return f"- {name} — {txt('Artist')}, {txt('LicenseShortName')}. https://commons.wikimedia.org/wiki/File:{uri.rsplit('/',1)[1]}"
with concurrent.futures.ThreadPoolExecutor(6) as pool:credits=list(pool.map(fetch,imgs.items()))
Path('SOURCES.md').write_text('# St. Louis 1904 / Boston 1905\n\nhttps://en.wikipedia.org/wiki/Athletics_at_the_1904_Summer_Olympics_%E2%80%93_Men%27s_marathon\n\nhttps://en.wikipedia.org/wiki/Frederick_Lorz\n\nArchival images cropped or placed in frames for vertical display. Other period scenes are editorial illustrations. Route graphic is schematic.\n\n'+'\n'.join(credits))
