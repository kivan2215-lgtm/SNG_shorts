from PIL import Image,ImageOps,ImageDraw
from functools import lru_cache
keys='loss lawyers jet ads flex arena diploma robe dad grip victory coat deal press jar paperwork raise accountant'.split()
animated=set(keys)
@lru_cache(None)
def base(k):
 i=keys.index(k); im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(750,1334),method=Image.Resampling.LANCZOS)
from PIL import ImageFont
import math
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
animated={'ads','grip','victory','jar','deal','accountant','jet','arena'}
def draw(k,t,ru):
 im=base(k).crop((15,27,735,1307))
 if k not in animated:return im
 d=ImageDraw.Draw(im); gold='#FFD477'; teal='#64E1D0'; ink='#142B32'
 def label(x,y,s,n=25,c='white'):d.text((x,y),s,font=font(n),fill=c,anchor='mm')
 def line(points,fill,width):d.line(points,fill=fill,width=width,joint='curve')
 u=min(1,t*1.8);u=u*u*(3-2*u)
 d.rounded_rectangle((54,690,666,864),24,fill=ink,outline='#8CB5AF',width=2)
 if k=='ads' or k=='deal':
  label(205,733,'SOUTHWEST',24);label(515,733,'STEVENS',24)
  for x in [205,515]:d.ellipse((x-7,769,x+7,783),fill=gold)
  for x in [205,515]:line([(x,776),(x+(360-x)*u,807)],teal,5)
  if u>.75:label(360,834,('ОБЩИЙ СЛОГАН' if ru else 'SHARED SLOGAN') if k=='deal' else ('ОДНА ИДЕЯ' if ru else 'ONE IDEA'),23,gold)
 elif k in ('grip','victory'):
  label(360,723,('ПОЕДИНОК' if ru else 'THE MATCH') if k=='grip' else ('ПОБЕДА STEVENS' if ru else 'STEVENS WINS'),27,gold)
  a=(202,823);b=(516,823);px=360+(75*u if k=='victory' else 16*math.sin(t*6));py=765+22*u if k=='victory' else 765
  line([a,(260,823),(px,py)],teal,14);line([b,(460,823),(px,py)],gold,14);d.ellipse((px-13,py-12,px+13,py+12),fill='white')
 elif k=='jar':
  label(360,720,'НА БЛАГОТВОРИТЕЛЬНОСТЬ' if ru else 'FOR CHARITY',25,gold)
  for i in range(5):
   x=245+i*58;y=750+int(65*((t*2+i/5)%1));d.ellipse((x-10,y-10,x+10,y+10),fill=gold);label(x,y,'$',13,ink)
  line([(204,800),(204,845),(518,845),(518,800)],teal,4)
 elif k=='accountant':
  label(360,720,'ТРЕНИРОВКА БУХГАЛТЕРА' if ru else 'PAYROLL WORKOUT',24,gold)
  for i in range(1+int(4*u)):
   y=832-i*19;d.rounded_rectangle((247+i*3,y-14,488+i*3,y),5,fill=[teal,gold][i%2]);d.ellipse((258,y-11,266,y-3),fill=ink)
 else:
  label(360,735,'ДАЛЛАС · 1992' if ru else 'DALLAS · 1992',34,gold)
  line([(150,804),(565,804)],'#78938E',3);x=150+415*u;d.ellipse((x-8,796,x+8,812),fill=teal)
 return im
