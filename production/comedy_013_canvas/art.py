from PIL import Image,ImageDraw,ImageOps,ImageFont
from functools import lru_cache
import math
keys='crate trolley worry cash plan smile opened canvas label crowd guard count pack call ledger court piles sign'.split()
animated={'crate','plan','label','count','ledger','piles','sign'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 im=im.crop((w*c//3+4,h*r//2+4,w*(c+1)//3-4,h*(r+1)//2-4))
 return ImageOps.fit(im,(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base(k).copy()
 if k not in animated:return im
 d=ImageDraw.Draw(im);u=min(1,t*1.65);u=u*u*(3-2*u); ivory='#fcf0d0';ink='#223e42';red='#a94130';gold='#cc9954'
 def card(x,y,w,h):
  d.rounded_rectangle((x+4,y+6,x+w+4,y+h+6),9,fill='#4a3c34');d.rounded_rectangle((x,y,x+w,y+h),9,fill=ivory,outline=ink,width=2)
 def label(x,y,s,n=28):d.text((x,y),s,font=font(n),fill=ink,anchor='mm')
 if k=='crate':
  y=round(716-12*u);card(64,y,250,96);label(191,y+34,'↑  ↑',29);label(191,y+70,'ХРУПКОЕ' if ru else 'FRAGILE',25)
 if k in ('plan','count'):
  card(55,675,610,180)
  for j in range(2):
   x=98+j*300;d.rectangle((x,698,x+210,801),fill=gold,outline=ink,width=3);d.rectangle((x+9,707,x+201,792),fill='#fffcf0')
   if k=='plan':
    for n in range(int(12*u)+1):
     dx=x+15+(n%4)*45;dy=714+(n//4)*22;d.rectangle((dx,dy,dx+39,dy+17),fill='#91b59b',outline=ink);d.ellipse((dx+16,dy+4,dx+23,dy+12),outline=ink)
   else:
    if u>(j+1)*.32:d.line([(x+79,750),(x+100,769),(x+131,725)],fill='#5d9674',width=6)
   label(x+105,828,(['ДАНИЯ','АВСТРИЯ'] if ru else ['DENMARK','AUSTRIA'])[j] if k=='plan' else str(j+1),20)
 if k=='label':
  x=round(68-590*(1-u));card(x,747,582,85);label(x+291,789,'«Бери деньги и беги»' if ru else 'Take the Money and Run',32)
 if k=='ledger':
  card(85,700,550,145);label(360,744,'НАЛИЧНЫЕ В РАМАХ' if ru else 'CASH IN FRAMES',26);d.line((115,773,605,773),fill=gold,width=3);label(360,807,'0 DKK' if u>.38 else '···',34)
 if k=='piles':
  card(75,690,570,160)
  for n in range(1+round(7*u)):
   y=791-8*n;d.rounded_rectangle((128,y,297,y+16),3,fill='#8dbc9a',outline=ink)
  d.rectangle((434,795,553,810),fill='#8dbc9a',outline=ink);label(210,828,'ВОЗВРАТ' if ru else 'REPAYMENT',19);label(498,828,'ГОНОРАР' if ru else 'FEE',19)
 if k=='sign':
  card(116,740,488,103);d.line((150,811,566,811),fill=gold,width=2)
  pts=[(162+int(i*3.4),796+int(14*math.sin(i*.29)*math.sin(i*.06)-18*math.exp(-((i-28)/5)**2))) for i in range(1+int(107*u))]
  if len(pts)>1:d.line(pts,fill=ink,width=4)
 return im
