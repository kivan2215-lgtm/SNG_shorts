from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
keys='finish shock passengers lake pack shoes bus rider driver return bronze rival solo vests rear clipboard medal podium'.split()
animated={'shock','lake','shoes','bus','bronze','clipboard','podium'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base(k).copy()
 if k not in animated:return im
 d=ImageDraw.Draw(im);gold='#ffc277';ink='#102f37';cream='#fff3d7';u=min(1,t*1.55);u=u*u*(3-2*u)
 def card():d.rounded_rectangle((66,688,654,862),18,fill=ink,outline='#849d93',width=2)
 def txt(x,y,s,n=26,col=cream):d.text((x,y),s,font=font(n),fill=col,anchor='mm')
 card()
 if k=='shock' or k=='clipboard':
  txt(360,723,('МЕСТО НА ФИНИШЕ' if ru else 'FINISH POSITION') if k=='shock' else ('ПОСЛЕ ПРОВЕРКИ' if ru else 'OFFICIAL RESULT'),24)
  vals=('3','4') if k=='shock' else ('4','3')
  txt(225,792,vals[0],62);d.line((295,792,295+135*u,792),fill=gold,width=4)
  if u>.9:d.polygon([(425,782),(443,792),(425,802)],fill=gold);txt(503,792,vals[1],62,gold)
 elif k in ('bus','podium'):
  txt(360,723,('АВТОБУС ДЛЯ ЗРИТЕЛЕЙ' if ru else 'SPECTATOR SHUTTLE') if k=='bus' else ('ДО ПЬЕДЕСТАЛА?' if ru else 'PODIUM STOP?'),25)
  d.line((145,818,573,818),fill='#77918c',width=3);x=round(123+362*u);d.rounded_rectangle((x,764,x+94,806),8,fill=gold)
  for i in range(3):d.rectangle((x+9+i*26,772,x+28+i*26,788),fill=ink)
  for a in (20,73):d.ellipse((x+a-8,796,x+a+8,812),fill=cream,outline=ink,width=3)
 elif k=='shoes':
  txt(360,720,'РИТМ БЕГА' if ru else 'RUNNING CADENCE')
  for j in range(8):
   x=149+j*60;y=790+12*(j%2);d.ellipse((x,y,x+27,y+14),fill=gold if j<1+round(7*u) else '#587578')
 elif k=='lake':
  txt(360,732,'KIELDER WATER  ·  2011',30);txt(360,805,'42,195 КМ' if ru else '26.2 MILES',40,gold)
 else:
  txt(360,720,'ПРЕДВАРИТЕЛЬНО' if ru else 'PROVISIONAL')
  for j,h in enumerate([38,55,25]):d.rectangle((216+j*96,837-h*u,306+j*96,837),fill=[cream,'#d2b55f','#b8835a'][j])
 return im
