from PIL import Image, ImageDraw, ImageFont, ImageOps
from functools import lru_cache
import math
keys='wheel street tire lawyer archaeologist barrow garden invoice sketch potter stamp trays judge cyclists bike accountant prize finale'.split()
animated={'wheel','drawing','diagram','stamp','trays','accountant','finale'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
@lru_cache(None)
def fig(n):
 im=Image.open('fig-'+str(n)+'.jpg');w,h=im.size
 return ImageOps.contain(im.crop((int(.25*w),int(.26*h),int(.76*w),int(.69*h))),(540,440))
def draw(k,t,ru):
 im=base({'drawing':'sketch','diagram':'barrow'}.get(k,k)).copy();d=ImageDraw.Draw(im)
 def label(x,y,s,n=27,fill='#fff2ca'):d.text((x,y),s,font=font(n),fill=fill,anchor='mm')
 def card(y,b):d.rounded_rectangle((66,y,654,b),18,fill='#183e41',outline='#e5ba68',width=2)
 u=min(1,t*1.7);u=u*u*(3-2*u)
 if k in ('drawing','diagram'):
  y=round(298+50*(1-u));card(y,y+557);p=fig(11 if k=='drawing' else 10);im.paste(p,((720-p.width)//2,y+64));label(360,y+32,'AU 2001100012',25);label(360,y+521,('РИС. 2' if ru else 'FIG. 2') if k=='drawing' else ('РИС. 1' if ru else 'FIG. 1'),23)
 elif k=='trays':
  card(672,850);label(222,718,'ФОРМА' if ru else 'FORM');label(505,718,'НОВИЗНА' if ru else 'NOVELTY')
  d.line((172,780,550,780),fill='#7f9f8c',width=4);x=round(200+308*u);d.rounded_rectangle((x-23,749,x+23,808),5,fill='#f9dd9d')
  for a in (766,779,792):d.line((x-13,a,x+13,a),fill='#1b434a',width=2)
 elif k=='stamp':
  y=round(746-95*(1-u)**2);card(y,y+74);label(360,y+37,'ПАТЕНТ ВЫДАН' if ru else 'PATENT GRANTED',33)
 elif k in ('wheel','finale','accountant'):
  if k=='accountant':card(696,845);label(360,730,'КОЛЁСА' if ru else 'WHEELS')
  count=4 if k=='accountant' else 1
  for j in range(count):
   cx=185+116*j if count==4 else 555;cy=790;r=30 if count==4 else 49
   if count==4 and (j+.2)/4>u:continue
   d.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#28484a',outline='#f0c26e',width=5)
   for s in range(8):
    a=t*2.1+s*math.pi/4;d.line((cx,cy,cx+(r-4)*math.cos(a),cy+(r-4)*math.sin(a)),fill='#ebc885',width=2)
 return im
