from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math
keys='edge gasp scientist dish tower march overhead ledge pencil floor kneel high committee legs award mop paper end'.split()
animated={'simulation','spin','tower','paper'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+5,r*h//2+5,(c+1)*w//3-5,(r+1)*h//2-5)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def draw(k,t,ru):
 im=base({'simulation':'pencil','spin':'high'}.get(k,k)).copy()
 if k not in animated:return im
 d=ImageDraw.Draw(im);dark='#103641';gold='#ffcc65';cream='#fff4d3';u=min(1,t*1.3)
 if k in ('simulation','spin'):
  d.rounded_rectangle((37,295,683,879),23,fill=dark,outline='#c49362',width=3)
  for x in range(65,660,38):d.line((x,399,x,805),fill='#1b4650')
  for y in range(400,805,38):d.line((65,y,660,y),fill='#1b4650')
  d.text((360,351),('ПАДЕНИЕ СО СТОЛА' if ru else 'OFF THE TABLE') if k=='simulation' else ('ПОЛНЫЙ ОБОРОТ' if ru else 'ONE FULL TURN'),font=font(29),fill=cream,anchor='mm')
  top=444 if k=='spin' else 600
  d.rectangle((65,top,288,top+18),fill='#ba7755');d.rectangle((93,top+18,110,803),fill='#a26850')
  d.line((65,807,658,807),fill='#c1d0c4',width=4)
  def loc(q):
   if q<.28:return (227+92*q/.28,top-15+10*q/.28,31*q/.28)
   v=(q-.28)/.72
   return (319+207*v,top-5+(790-top+5)*v*v,31+(149 if k=='simulation' else 329)*v)
  trail=[loc(u*i/32)[:2] for i in range(33)];d.line(trail,fill='#87ac9e',width=3)
  cx,cy,angle=loc(u);a=math.radians(angle)
  def poly(pts):return [(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)) for x,y in pts]
  d.polygon(poly([(-54,-10),(54,-10),(54,10),(-54,10)]),fill='#dea665',outline='#ffdea2')
  d.polygon(poly([(-36,-14),(40,-14),(40,-10),(-36,-10)]),fill=gold)
  d.text((360,843),('масло' if ru else 'butter')+'  ▰',font=font(21),fill=gold,anchor='mm')
 elif k=='paper':
  d.rounded_rectangle((108,753,611,838),12,fill=dark);d.text((360,797),'IG NOBEL   /   1996',font=font(34),fill=gold,anchor='mm')
 elif k=='tower':
  for j in range(1+round(5*u)):
   d.rounded_rectangle((522,807-16*j,602,822-16*j),4,fill=gold,outline='#b68f4e')
 return im
