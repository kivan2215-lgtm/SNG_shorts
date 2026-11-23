from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import math,json
keys='wheels laugh ask london ticket taxi pilots radar runway castle plan papers hands mapgirl fuel train seat exit'.split()
animated={'wheels','radar','map','hands','return','exit'}
@lru_cache(None)
def base(k):
 i=keys.index(k);im=Image.open('ABC'[i//6]+'.png').convert('RGB');w,h=im.size;c=i%3;r=i%6//3
 return ImageOps.fit(im.crop((c*w//3+4,r*h//2+4,(c+1)*w//3-4,(r+1)*h//2-4)),(720,1280),method=Image.Resampling.LANCZOS)
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def proj(x,y):return (int(38+(x+7)*47),int(710-(y-49)*77))
cities=[proj(-.05,51.5),proj(-3.2,55.95),proj(6.77,51.23)]
@lru_cache(None)
def chart():
 im=Image.new('RGB',(720,800),'#15394b');d=ImageDraw.Draw(im)
 for ring in json.load(open('coast.json')):d.polygon([proj(*p[:2]) for p in ring],fill='#497074',outline='#9bb8aa')
 return im
def draw(k,t,ru):
 u=min(1,t*1.45);u=u*u*(3-2*u)
 if k in ('map','return'):
  im=base('papers' if k=='map' else 'fuel').copy();m=chart().copy();d=ImageDraw.Draw(m)
  def trail(a,b,f,color):
   pts=[]
   for j in range(1+int(70*f)):
    v=j/70;pts.append((a[0]+(b[0]-a[0])*v,a[1]+(b[1]-a[1])*v-25*math.sin(math.pi*v)))
   if len(pts)>1:d.line(pts,fill=color,width=6)
   return pts[-1]
  l,e,g=cities;trail(l,g,1,'#94c4bb');p=trail(e,g,u,'#ffca65') if k=='return' else trail(l,e,u,'#ffca65')
  for (x,y),name,dx in zip(cities,(['Лондон','Эдинбург','Дюссельдорф'] if ru else ['London','Edinburgh','Düsseldorf']),[0,12,-60]):
   d.ellipse((x-6,y-6,x+6,y+6),fill='white');d.text((x+dx,y+28),name,font=font(23),anchor='mm',fill='white',stroke_width=2,stroke_fill='#183649')
  x,y=p;d.ellipse((x-9,y-9,x+9,y+9),fill='#ffca65');d.text((28,34),('ПОВТОРНЫЙ ВЫЛЕТ' if ru else 'SECOND DEPARTURE') if k=='return' else ('БИЛЕТ И ПЛАН ПОЛЁТА' if ru else 'TICKET AND FLIGHT PLAN'),font=font(30),fill='white')
  im.paste(m,(0,105));return im
 im=base(k).copy();d=ImageDraw.Draw(im)
 if k=='hands':
  d.rounded_rectangle((80,704,640,827),18,fill='#123747');d.text((360,740),'КОМУ В ГЕРМАНИЮ?' if ru else 'WHO WANTS GERMANY?',font=font(28),anchor='mm',fill='white')
  for i in range(14):
   x=109+i*37;v=min(1,max(0,(t*2.5-i*.065)*4));y=int(804-33*v)
   d.rounded_rectangle((x,y,x+21,818),5,fill='#efae62' if v else '#4d7479')
 elif k=='radar':
  cx,cy=534,750;d.ellipse((cx-66,cy-66,cx+66,cy+66),fill='#173b44',outline='#81d3ac',width=2)
  ang=-2.8+t*5;d.line((cx,cy,cx+59*math.cos(ang),cy+59*math.sin(ang)),fill='#81d3ac',width=3);d.ellipse((548,717,555,724),fill='#ffe3a5')
 elif k=='exit' and t>.6:
  d.rounded_rectangle((185,730,535,803),14,fill='#224346');d.text((360,767),'ВЫХОДИТЬ?' if ru else 'GET OFF HERE?',font=font(30),anchor='mm',fill='white')
 return im
