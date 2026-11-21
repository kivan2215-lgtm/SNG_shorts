from PIL import Image,ImageOps,ImageDraw,ImageFont
from functools import lru_cache
import math
W,H=720,1280
ink='#112f38';cream='#fff0cd';amber='#ffc45c';red='#bb472d';aqua='#8dd6c2'
names='park dent phone whale crew gull tv plume up wreck depart manager'.split()
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 if k=='geo':return Image.open('beach.jpg').convert('RGB')
 i=names.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB')
 w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+3,i//3*h+3,(i%3+1)*w-3,(i//3+1)*h-3))
@lru_cache(None)
def fit(k,w,h):return ImageOps.fit(panel(k),(w,h),centering=(.50,.40))
def put(d,x,y,s,n,c=cream):d.text((x,y),s,font=font(n),fill=c)
@lru_cache(None)
def still(k,ru):
 pairs={'park':'phone','whale':'crew','crew':'whale','tv':'up','up':'plume','wreck':'park','manager':'depart','geo':'whale','depart':'manager'}
 if k not in pairs:return fit(k,W,H)
 im=Image.new('RGB',(W,H),ink);im.paste(fit(k,W,870),(0,0));im.paste(fit(pairs[k],W,402),(0,878))
 if k=='geo':
  d=ImageDraw.Draw(im);d.rectangle((22,700,641,849),fill=ink)
  put(d,41,714,'Орегон · Ноябрь 1970' if ru else 'Oregon · November 1970',39);put(d,43,785,'Флоренс, 2013 · Jsayre64 · CC BY-SA 3.0' if ru else 'Florence, 2013 · Jsayre64 · CC BY-SA 3.0',22)
 return im
animated={'before','after','claim','roster','pay','birdexit','report'}
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
@lru_cache(76)
def model(n):
 return Image.open('car/%04d.jpg'%n).convert('RGB').resize((720,780),Image.Resampling.LANCZOS)
@lru_cache(56)
def bird_frame(n):
 import time
 from pathlib import Path
 p=Path('bird/%04d.jpg'%n)
 while not p.exists():time.sleep(.4)
 for attempt in range(4):
  try:return Image.open(p).convert('RGB').resize((720,627),Image.Resampling.LANCZOS)
  except OSError:
   if attempt==3:raise
   time.sleep(.25)
def draw(k,t,ru):
 if k not in animated:return still(k,ru)
 w=lambda a,b:a if ru else b
 im=Image.new('RGB',(W,H),ink);d=ImageDraw.Draw(im)
 if k in ('before','after'):
  f=round(1+30*t) if k=='before' else round(30+42*t)
  im.paste(model(f),(0,52));d.line((37,835,676,835),fill=aqua,width=3)
  put(d,38,850,w('Стоянка у моря','Coastal parking lot') if k=='before' else w('Крыша автомобиля','Vehicle roof'),43)
  if k=='after' and f>=48:
   d.line((334,433,430,304,595,304),fill=amber,width=4);d.ellipse((328,427,340,439),fill=amber)
  return im
 bg={'claim':'phone','roster':'gull','pay':'gull','birdexit':'depart','report':'manager'}[k];im.paste(fit(bg,W,690),(0,0))
 if k in ('pay','birdexit'):
  im.paste(bird_frame(1+round(51*t)),(0,60))
 if k=='claim':
  put(d,40,715,w('Страховой случай','Insurance claim'),43);d.line((40,794,675,794),fill=aqua,width=3)
  s=w('Причина: кит','Cause: whale');put(d,40,810,s[:int(smooth(t*1.5)*len(s))],48,amber)
 elif k in ('roster','pay','birdexit'):
  put(d,40,714,w('Бригада уборки','Clean-up crew'),42);d.line((40,782,675,782),fill=aqua,width=3)
  s={'roster':w('Чайки','Seagulls'),'pay':w('Оплата: обед','Pay: lunch'),'birdexit':w('На смене: никого','On duty: nobody')}[k]
  x=int(38-710*(1-smooth(t*2.8)));d.rounded_rectangle((x,798,x+636,888),9,fill=amber if k!='birdexit' else red);put(d,x+21,812,s,43,ink if k!='birdexit' else cream)
 else:
  for j,(a,b) in enumerate([('Кит остался','Whale still there'),('Машина разбита','Car wrecked'),('Чайки ушли','Gulls gone')]):
   y=697+j*74;x=round(35-715*(1-smooth(4*t-j)));d.rounded_rectangle((x,y,x+646,y+63),6,fill=cream if j==0 else amber if j==1 else red);put(d,x+22,y+7,w(a,b),36,ink if j<2 else cream)
 return im
