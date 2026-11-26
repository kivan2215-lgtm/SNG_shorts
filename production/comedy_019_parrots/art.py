from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
keys='star shocked chuckle park keeper five curse laugh chorus tourist worried grandad move calm class ticket crowd bowl'.split()
animated={'curse','laugh','chorus','class','bowl'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base(k).copy()
 if k not in animated:return im
 d=ImageDraw.Draw(im);ink='#123a35';gold='#ffcf76';cream='#fcf2d0';u=min(1,t*1.8);u=u*u*(3-2*u)
 def txt(x,y,s,n=26):d.text((x,y),s,font=font(n),fill=cream,anchor='mm')
 if k in ('curse','laugh'):
  x=round(398+20*(1-u));y=690;d.rounded_rectangle((x,y,x+237,y+87),28,fill=ink,outline=gold,width=3)
  d.polygon([(x+20,y+85),(x+12,y+101),(x+57,y+84)],fill=ink)
  txt(x+118,y+43,('ХА-ХА!' if ru else 'HA HA!') if k=='laugh' else '#@&*!',34)
 elif k in ('chorus','class'):
  d.rounded_rectangle((65,696,655,857),19,fill=ink,outline=gold,width=2)
  txt(360,730,('ОДИН МАТЕРИТСЯ' if ru else 'ONE SWEARS') if k=='chorus' else ('ПО РАЗНЫМ ВОЛЬЕРАМ' if ru else 'SEPARATE AVIARIES'),23)
  for j in range(5):
   x=145+105*j;y=799
   if k=='class':
    x=int(360+(x-360)*u);d.rounded_rectangle((x-42,y-33,x+42,y+38),8,outline=gold,width=2)
   hop=int(9*math.sin(2*math.pi*(t*2-j*.15))) if k=='chorus' and j>0 else 0;y+=hop
   d.ellipse((x-20,y-19,x+18,y+19),fill=('#eb9a50' if j==0 else '#a6b5ad'));d.polygon([(x+11,y-5),(x+28,y+1),(x+13,y+7)],fill='#2b2520');d.ellipse((x+4,y-9,x+10,y-3),fill='black')
 else:
  for j in range(9):
   f=(t*2+j*.13)%1;x=547+int(16*math.sin(j*3));y=int(681+114*f*f);d.ellipse((x,y,x+5,y+9),fill=gold)
  d.pieslice((501,769,596,830),0,180,fill='#955b40',outline=gold,width=2)
 return im
