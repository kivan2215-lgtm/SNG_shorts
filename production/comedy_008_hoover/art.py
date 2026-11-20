from functools import lru_cache
from PIL import Image,ImageOps,ImageDraw,ImageFont
import math
W,H=720,1280
ink='#0b3441';paper='#fff2cf';red='#ba3c27';gold='#edb849';blue='#95d6ce'
names='shop receipt flight boss queue news broken repair van boarding warehouse cloth'.split()
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 if k=='museum':return Image.open('museum.jpg').convert('RGB')
 i=names.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB')
 w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+3,i//3*h+3,(i%3+1)*w-3,(i//3+1)*h-3))
@lru_cache(None)
def fit(k,w,h):return ImageOps.fit(panel(k),(w,h),centering=(.5,.43))
def label(d,x,y,s,n,color=paper):d.text((x,y),s,font=font(n),fill=color)
@lru_cache(None)
def scene(k,ru):
 if k=='museum':
  im=Image.new('RGB',(W,H),paper);pic=ImageOps.contain(panel(k),(670,700));im.paste(pic,((W-pic.width)//2,128));d=ImageDraw.Draw(im);label(d,32,842,'Hoover · 1990',42,ink);label(d,32,896,'Rama · CC BY-SA 2.0 FR',21,ink);return im
 pairs={'shop':('shop','receipt'),'abandoned':('warehouse','shop'),'seller':('shop','receipt'),'repair':('repair','broken'),'walk':('van','repair'),'broken':('broken','flight'),'van':('van','repair'),'dust':('warehouse','cloth')}
 if k not in pairs:return fit(k,W,H)
 a,b=pairs[k];im=Image.new('RGB',(W,H),ink);im.paste(fit(a,W,864),(0,0));im.paste(fit(b,W,408),(0,872));return im
animated={'deal','math','checkin','claims','post','washplane','passengers','bill','walk','dust'}
def ease(v):
 v=min(1,max(0,v));return v*v*(3-2*v)
def plane(d,x,y):
 d.polygon([(x-33,y+2),(x-12,y-4),(x-3,y-32),(x+4,y-33),(x+3,y-5),(x+35,y-2),(x+41,y+3),(x+3,y+8),(x-2,y+28),(x-8,y+29),(x-11,y+8),(x-33,y+12)],fill=red)
def draw(k,t,ru):
 word=lambda r,e:r if ru else e
 if k not in animated:return scene(k,ru)
 if k=='dust':
  im=scene(k,ru).copy();d=ImageDraw.Draw(im)
  for j in range(30):
   x=(j*83+round(40*t))%710;y=(j*71+round(62*t))%825
   d.ellipse((x,y,x+2+j%3,y+2+j%3),fill='#efdcad')
  return im
 if k=='walk':
  im=scene(k,ru).copy();d=ImageDraw.Draw(im);d.rectangle((0,680,720,863),fill=ink)
  label(d,40,690,word('Фургон остался','The van stays'),33)
  for j in range(int(t*11)+1):
   x=39+j*57;y=773+15*(j%2);d.ellipse((x,y,x+25,y+10),fill=gold)
  return im
 bg={'deal':'receipt','math':'boss','checkin':'queue','claims':'news','post':'news','washplane':'broken','passengers':'boarding','bill':'boss'}[k]
 im=Image.new('RGB',(W,H),ink);im.paste(fit(bg,W,670),(0,0));d=ImageDraw.Draw(im)
 if k=='deal':
  x=int(36-370*(1-ease(t*2)));d.rounded_rectangle((x,694,x+645,885),14,fill=paper)
  d.line((x+466,701,x+466,878),fill=red,width=3)
  label(d,x+20,710,word('Британия → США','Britain → USA'),36,ink);label(d,x+20,775,word('Туда и обратно','Return flights'),30,ink);label(d,x+492,732,'×2',59,red)
 elif k=='math':
  for j,(v,a,b) in enumerate([(100,'Покупка','Purchase'),(600,'Авиабилеты','Flights')]):
   y=692+j*106;label(d,33,y,word(a,b),32);label(d,494,y,'£'+str(v),36,gold)
   u=ease(2*t-j*.85);d.rectangle((35,y+57,36+int(635*u*v/600),y+78),fill=blue if not j else gold)
 elif k=='checkin':
  label(d,36,697,word('Касса аэропорта','Airport check-in'),46);d.line((40,818,640,818),fill=blue,width=5);plane(d,76+int(519*ease(t)),817)
 elif k=='post':
  label(d,38,685,word('Заявка отправлена','Claim in the post'),42)
  # Slide the envelope into a Royal Mail style pillar box and occlude it under the lip.
  d.rounded_rectangle((483,761,650,910),18,fill=red)
  d.rectangle((499,794,631,818),fill=ink)
  x=int(38+500*ease(t));y=int(832-30*ease(t))
  d.rectangle((x,y-34,x+129,y+34),fill=paper,outline=ink,width=3)
  d.line((x,y-34,x+65,y+5,x+129,y-34),fill=red,width=3)
  d.rectangle((538,789,645,850),fill=red)
 elif k=='claims':
  label(d,42,687,word('Заявки на перелёт','Flight claims'),42)
  for j in range(1+int(8*ease(t))):
   x=42+j*57;y=785+(j%2)*13;d.rectangle((x,y,x+143,y+75),fill=paper,outline=ink,width=3);d.line((x,y,x+72,y+44,x+143,y),fill=red,width=3)
 elif k=='washplane':
  label(d,38,694,word('Стиралка → Америка?','Washing machine → USA?'),39);d.line((46,814,662,814),fill=gold,width=3);plane(d,76+410*ease(t),812)
 elif k=='passengers':
  label(d,35,687,word('Слетали по акции','People who flew'),39);label(d,31,753,'≈ '+format(round(220*ease(1.7*t))*1000,',').replace(',', ' ' if ru else ','),66,gold)
 else:
  label(d,38,688,word('Цена всей акции','Total cost to Hoover'),41);label(d,35,758,'£'+format(round(48*ease(1.6*t))*1000000,',').replace(',', ' ' if ru else ','),65,gold)
 return im
