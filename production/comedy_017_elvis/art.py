from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
keys='plane pen landing gate runner hotel application fans badge desk doorway shop aide beatles talk order box accountant'.split()
animated={'letter','hotel','shop','path','photo'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+5,r*h//2+5,(c+1)*w//3-5,(r+1)*h//2-5)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
@lru_cache(None)
def archive(name,w,h):
 return ImageOps.contain(Image.open(name).convert('RGB'),(w,h),method=Image.Resampling.LANCZOS)
def draw(k,t,ru):
 ink='#15332f';gold='#dfbf79';paper='#f5e7c6';u=min(1,t*1.8);u=u*u*(3-2*u)
 if k=='photo':
  im=Image.new('RGB',(720,1280),ink);d=ImageDraw.Draw(im);orig=archive('photo.jpg',700,760);y=322;d.rectangle((5,y-5,715,y+orig.height+5),fill=paper);im.paste(orig,((720-orig.width)//2,y));d.text((360,247),'21   XII   1970',anchor='mm',font=font(36),fill=gold);d.text((360,855),'WHITE HOUSE  /  NARA  ·  1634221',font=font(19),anchor='mm',fill=paper);return im
 im=base({'letter':'pen','path':'order','badge':'pen'}.get(k,k)).copy();d=ImageDraw.Draw(im)
 if k=='badge':
  d.rounded_rectangle((67,312,653,840),26,fill=ink,outline=gold,width=4)
  d.polygon([(360,362),(477,400),(464,534),(430,594),(360,642),(290,594),(256,534),(243,400)],fill=gold)
  d.polygon([(360,386),(455,418),(445,525),(417,581),(360,620),(303,581),(275,525),(265,418)],fill=ink)
  d.text((360,506),'BNDD',font=font(38),fill=gold,anchor='mm')
  for j,st in enumerate(('ФЕДЕРАЛЬНОЕ БЮРО','ПО НАРКОТИКАМ') if ru else ('BUREAU OF NARCOTICS','AND DANGEROUS DRUGS')):
   d.text((360,701+j*49),st,font=font(28),fill=paper,anchor='mm')
 elif k=='letter':
  y=int(124+66*(1-u));p=archive('letter.jpg',586,750);d.rectangle((357-p.width//2,y-4,363+p.width//2,y+p.height+5),fill=gold);im.paste(p,((720-p.width)//2,y))
 elif k=='shop':
  cx,cy=555,732;r=90;d.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#101b23',outline=gold,width=3)
  for rr in range(39,85,8):d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline='#34434b')
  d.ellipse((cx-28,cy-28,cx+28,cy+28),fill='#ac463e');a=t*6;d.line((cx,cy,cx+21*math.cos(a),cy+21*math.sin(a)),fill=gold,width=4)
 elif k=='hotel':
  x,y=543,730;r=58;d.ellipse((x-r,y-r,x+r,y+r),fill=paper,outline=gold,width=4)
  for j in range(12):
   a=j*math.pi/6;d.line((x+47*math.cos(a),y+47*math.sin(a),x+52*math.cos(a),y+52*math.sin(a)),fill=ink,width=3)
  a=-2+t*1.4;d.line((x+22,y-20,x,y,x+42*math.cos(a),y+42*math.sin(a)),fill=ink,width=5)
 elif k=='path':
  d.rounded_rectangle((50,723,670,850),19,fill=ink,outline=gold,width=2)
  for j,s in enumerate(('ПИСЬМО','ВСТРЕЧА','ЖЕТОН') if ru else ('LETTER','MEETING','BADGE')):
   x=159+j*201;d.text((x,765),s,font=font(24),anchor='mm',fill=paper)
   if j<2:d.line((x,811,x+201,811),fill='#827961',width=3)
   d.ellipse((x-8,803,x+8,819),fill=gold)
  x=159+402*u;d.ellipse((x-11,800,x+11,822),fill='#f69a6a')
 return im
