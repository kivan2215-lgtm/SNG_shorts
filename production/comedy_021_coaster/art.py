from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
keys='rider curious bag doctor coaster notes model stones walk holiday scream check front rear results insurance fare award'.split()
animated={'coaster','stones','rides','front','rear','both','fare','award'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base({'rides':'scream','both':'results'}.get(k,k)).copy()
 if k not in animated:return im
 d=ImageDraw.Draw(im);ink='#143642';gold='#ffc072';cream='#fff3d6';blue='#74cdd0';u=min(t*2,1);u=u*u*(3-2*u)
 def text(x,y,s,n=24,color=cream):d.text((x,y),s,font=font(n),fill=color,anchor='mm')
 def panel(top=672):d.rounded_rectangle((52,top,668,856),20,fill=ink,outline=gold,width=2)
 if k in ('front','rear','both'):
  panel(570);text(360,605,'ВЫХОД КАМНЕЙ В МОДЕЛИ' if ru else 'STONE PASSAGE IN MODEL',26)
  for j,(v,total) in enumerate(((4,24),(23,36))):
   if j and k=='front':continue
   y=662+103*j;active=u if k in ('front','rear') and ((j==0 and k=='front') or (j==1 and k=='rear')) else 1
   text(165,y,('СПЕРЕДИ' if ru else 'FRONT') if j==0 else ('СЗАДИ' if ru else 'REAR'),22)
   text(473,y,f'{v} / {total}',32,gold)
   d.rounded_rectangle((100,y+26,616,y+45),8,fill='#416270')
   d.rounded_rectangle((100,y+26,100+max(2,516*v/total*active),y+45),6,fill=blue if j==0 else gold)
 elif k in ('coaster','rides'):
  panel();text(360,708,('20 ПОЕЗДОК' if ru else '20 RIDES') if k=='rides' else 'BIG THUNDER MOUNTAIN',26)
  pts=[(90+5*i,790-30*math.sin(i/15)) for i in range(108)];d.line(pts,fill=gold,width=4)
  for j in range(3):
   x,y=pts[min(107,int(90*t)+j*4)];d.rounded_rectangle((x-9,y-14,x+8,y-2),4,fill=blue)
 elif k=='stones':
  panel();text(360,715,'3 НАСТОЯЩИХ КАМНЯ' if ru else '3 REAL STONES')
  for j in range(3):
   if (j+.2)/3>u:continue
   x=220+j*140;r=12+5*j;d.polygon([(x-r,775),(x,766),(x+r,777),(x+r-3,793),(x-6,798)],fill=gold)
 elif k=='fare':
  panel(736);text(360,795,'ДЕТСКИЙ БИЛЕТ?' if ru else 'CHILD FARE?',30)
 else:
  panel(745);text(360,800,'IG NOBEL  /  2018',32,gold)
 return im
