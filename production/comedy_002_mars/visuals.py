from pathlib import Path
from functools import lru_cache
import math,os
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent;BG='#102029';CREAM='#fff0d1';GOLD='#ffcf58';RED='#ff8069';CYAN='#8addce'
@lru_cache(100)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=42,fill=CREAM,anchor='mm',width=940):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>24:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+12)),l,font=font(size),fill=fill,anchor=anchor)
def card(d,xy,s,col=GOLD,size=40):
 lines=s.split('\n');w=min(980,max(font(size).getlength(l) for l in lines)+40);h=len(lines)*(size+12)+20;x,y=xy;d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=18,fill=BG,outline=col,width=3);text(d,xy,s,size,col,width=w-30)
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def arrow(d,a,b,col=CYAN):
 d.line([a,b],fill=col,width=6);q=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-20*math.cos(q-.5),b[1]-20*math.sin(q-.5)),(b[0]-20*math.cos(q+.5),b[1]-20*math.sin(q+.5))],fill=col)
@lru_cache(30)
def source(n):return Image.open(P/'assets'/n).convert('RGB')
def contain(im,box=(25,160,1055,1770)):
 out=Image.new('RGB',(1080,1920),BG);x,y,x1,y1=box;s=min((x1-x)/im.width,(y1-y)/im.height);im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);out.paste(im,(round((x+x1-im.width)/2),round((y+y1-im.height)/2)));return out
@lru_cache(20)
def art(n,i):
 im=source(f'scenes{n}.png');w,h=im.size;return contain(im.crop((i%2*w//2,i//2*h//2,(i%2+1)*w//2,(i//2+1)*h//2)))
@lru_cache(70)
def model(k,i):
 f=P/'frames'/k/f'{i:04}.jpg'
 if not f.exists():
  if os.getenv('RENDER_FINAL')=='1':raise FileNotFoundError(f)
  fs=list((P/'frames'/k).glob('*.jpg'));f=min(fs,key=lambda x:abs(int(x.stem)-i))
 return Image.open(f).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
ART={'hook':(1,0),'reaction':(1,1),'coordination':(2,1),'calculations':(1,2),'teams':(3,0),'silence':(3,2),'forecast':(1,1),'thruster':(1,3),'banana':(2,0),'facepalm':(3,3),'restaurant':(2,2),'communication':(3,0),'vip':(2,3),'door':(2,3),'belief':(3,3),'question':(3,3)}
PHOTOS={'launch':'KSC-98pc1840.jpg','mission':'KSC-98pc1736.jpg','journey':'KSC-98pc1837.jpg','uncrewed':'KSC-98pc1083.jpg'}
def render(lang,k,p=0,seconds=None):
 tr=lambda a,b:b if lang=='en' else a;sec=p*3 if seconds is None else seconds
 if k in ART:im=art(*ART[k]).copy()
 elif k in PHOTOS:im=contain(source(PHOTOS[k]))
 elif k in ['report','report2']:
  im=contain(source('report_root.png').crop((180,610,1235,1220)),(45,440,1035,1300))
 elif k in ['units_a','units_b','transfer','factor','checks']:im=model('units',0).copy()
 elif k in ['approach','drift','lowpass','lost']:
  idx=round(min(1,sec/2)*60) if k=='lowpass' else (60 if k=='lost' else 0);im=model('orbit',idx).copy()
 else:raise ValueError(k)
 if k in ART or k in PHOTOS:
  over=Image.new('RGBA',im.size);d=ImageDraw.Draw(over)
  for y in range(1360,1920):d.line((0,y,1080,y),fill=(10,24,26,int(195*min(1,(y-1360)/310))))
  im=Image.alpha_composite(im.convert('RGBA'),over).convert('RGB')
 d=ImageDraw.Draw(im)
 if k=='launch':card(d,(540,1270),'11.12.1998',CYAN,42)
 if k=='journey':card(d,(540,1250),tr('9 МЕСЯЦЕВ ПОЛЁТА','9 MONTHS IN SPACE'),CYAN,40)
 if k=='silence':card(d,(540,1290),tr('СИГНАЛ ПОТЕРЯН','CONTACT LOST'),RED,42)
 if k=='forecast':card(d,(540,1320),tr('ПРОГНОЗ: ПИЗДЕЦ','FORECAST: SHITSHOW'),GOLD,40)
 if k in ['report','report2']:card(d,(540,1350),tr('ОШИБКА + ПРОВАЛ ПРОВЕРОК','ERROR + FAILED CHECKS'),CYAN,34)
 if k in ['units_a','units_b','transfer','factor']:
  card(d,(260,830),'lbf·s',GOLD,52)
  card(d,(790,1050),'?' if k=='units_a' else 'N·s',CYAN,52)
  if k=='units_a':card(d,(540,1290),tr('ПРОГРАММА A: ИМПУЛЬС','PROGRAM A: IMPULSE'),GOLD,34)
  if k=='units_b':card(d,(540,1290),tr('ПРОГРАММА B ЖДАЛА ДРУГИЕ ЕДИНИЦЫ','PROGRAM B EXPECTED DIFFERENT UNITS'),CYAN,31)
  if k=='transfer':
   u=ease(sec/1.2);x=320+360*u;y=1010+140*u;card(d,(x,y),'1',RED,40);card(d,(540,1340),tr('ЧИСЛО ПЕРЕДАЛИ БЕЗ ПЕРЕВОДА','NUMBER SENT WITHOUT CONVERSION'),RED,31)
  if k=='factor':
   card(d,(540,1260),'1 lbf·s ≈ 4.45 N·s',GOLD,48)
   u=ease(sec/1.0);d.rounded_rectangle((190,1330,190+round(650*u),1360),radius=10,fill=CYAN)
 if k in ['approach','drift','lowpass','lost']:
  if k!='approach':
   card(d,(540,520),tr('РАСЧЁТНЫЙ ПРОХОД','CALCULATED PASS'),CYAN,34)
   card(d,(540,1320),tr('ФАКТИЧЕСКИ — СЛИШКОМ НИЗКО','ACTUAL PASS: TOO LOW'),RED,33)
  if k=='drift':
   u=ease(sec/1.5);arrow(d,(540,585),(540,585+round(100*u)),RED)
  if k=='lost':card(d,(540,1130),tr('МИССИЯ ПОТЕРЯНА','MISSION LOST'),RED,42)
 if k=='checks':
  for i,label in enumerate([tr('ДАННЫЕ','DATA'),tr('ПРОВЕРКА','CHECK'),tr('РАСЧЁТ','MODEL')]):
   x=220+i*320;card(d,(x,1260),label,CYAN,30)
   if i<2:arrow(d,(x+100,1260),(x+200,1260))
  x=220+640*ease(sec/1.6);card(d,(x,1370),tr('ОШИБКА','ERROR'),RED,30)
 if k=='door':card(d,(540,1300),tr('КОНТРОЛЬ ПРОЙДЕН?','QUALITY CONTROL?'),RED,36)
 if k=='uncrewed':card(d,(540,1320),tr('БЕЗ ЭКИПАЖА','UNCREWED'),CYAN,40)
 return im
