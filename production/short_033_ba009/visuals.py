from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,json,random
P=Path(__file__).parent
WHITE='#f5f3e9';GOLD='#ffcf79';CYAN='#77dceb';RED='#ff8a7e';GREEN='#91e9b6';BG='#081722'
@lru_cache(80)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=40,fill=WHITE,anchor='mm',width=920):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>20:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+10)),l,font=font(size),fill=fill,anchor=anchor)
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def arrow(d,a,b,col=CYAN,w=4):
 d.line([a,b],fill=col,width=w);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-18*math.cos(ang-.45),b[1]-18*math.sin(ang-.45)),(b[0]-18*math.cos(ang+.45),b[1]-18*math.sin(ang+.45))],fill=col)
def tag(d,xy,label,col=WHITE,size=35):
 lines=label.split('\n');w=max(font(size).getlength(s) for s in lines)+28;h=len(lines)*(size+8)+14;x,y=xy
 d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=12,fill=BG,outline='#3a5665',width=2);text(d,xy,label,size,col)
def lead(d,xy,point,label,col=GOLD):
 x,y=xy;px,py=point;d.line([(x,y+34),(x,py-25),point],fill=col,width=3);d.ellipse((px-7,py-7,px+7,py+7),outline=col,width=3);tag(d,xy,label,col)
@lru_cache(24)
def model(kind,i):return Image.open(P/'frames'/kind/f'{i:04d}.jpg').convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
@lru_cache(20)
def index(kind):return json.loads((P/'frames'/kind/'index.json').read_text())
@lru_cache(8)
def photo(kind):return Image.open(P/'assets'/f'{kind}.jpg').convert('RGB')
def head(d,title,sub=''):
 d.rounded_rectangle((64,165,120,173),radius=3,fill=GOLD);text(d,(65,220),title,45,WHITE,'lm',930)
 if sub:text(d,(65,285),sub,29,'#b5c8ce','lm',930)
def archive(kind,lang):
 im=Image.new('RGB',(1080,1920),BG);pic=photo(kind).copy();pic.thumbnail((1000,830));im.paste(pic,((1080-pic.width)//2,480+(830-pic.height)//2));return im
TITLES={
'fail':('ОДИН ЗА ДРУГИМ…','ONE AFTER ANOTHER…'), 'alloff':('ОСТАНОВИЛИСЬ ВСЕ ЧЕТЫРЕ','ALL FOUR ENGINES STOPPED'),
'glow':('СТРАННОЕ СВЕЧЕНИЕ','A STRANGE BLUE GLOW'),'question':('ЧТО ПРОИСХОДИТ?','WHAT IS HAPPENING?'),
'archive':('24 ИЮНЯ 1982','24 JUNE 1982'),'cabin':('ДЫМ В САЛОНЕ','SMOKE IN THE CABIN'),'glide':('ТЯГИ НЕТ. ВЫСОТА УХОДИТ.','NO THRUST. LOSING ALTITUDE.'),
'attempt':('ПЕРЕЗАПУСК НЕ УДАЁТСЯ','RESTART ATTEMPTS FAIL'),'ocean':('ВНИЗУ — ОКЕАН','THE OCEAN BELOW'),'turn':('ПРИЧИНА БЫЛА ДРУГОЙ','SOMETHING ELSE WAS WRONG'),
'volcano':('ОБЛАКО ВУЛКАНИЧЕСКОГО ПЕПЛА','A CLOUD OF VOLCANIC ASH'),'radar':('РАДАР НЕ ПОКАЗАЛ ОПАСНОСТЬ','RADAR DID NOT REVEAL IT'),
'deposit':('ПЕПЕЛ ПОПАДАЕТ В ДВИГАТЕЛЬ','ASH ENTERS THE ENGINE'),'blocked':('ВОЗДУШНЫЙ ПОТОК НАРУШЕН','AIRFLOW IS DISRUPTED'),
'escape':('СНИЖЕНИЕ ВЫВОДИТ ИЗ ОБЛАКА','DESCENDING OUT OF THE ASH'),'clear':('ОТЛОЖЕНИЯ ОСТЫВАЮТ','THE DEPOSITS COOL'),
'restart':('ДВИГАТЕЛИ ЗАПУСКАЮТСЯ','THE ENGINES RESTART'),'oneoff':('ОДИН СНОВА ОТКЛЮЧИЛИ','ONE IS SHUT DOWN AGAIN'),
'cockpit':('ПОЛОСУ ПОЧТИ НЕ ВИДНО','THE RUNWAY IS HARD TO SEE'),'landing':('ПОСАДКА В ДЖАКАРТЕ','LANDING IN JAKARTA'),
'safe':('ВСЕ НА БОРТУ ВЫЖИЛИ','EVERYONE ON BOARD SURVIVED'),'evidence':('СЛЕДЫ ТОЙ НОЧИ','EVIDENCE OF THAT NIGHT')}
MAPPING={'fail':'flight','alloff':'flight','glow':'glow','question':'flight','cabin':'cabin','glide':'glide','attempt':'flight','ocean':'glide','turn':'flight','radar':'radar','deposit':'deposit','blocked':'blocked','escape':'glide','clear':'clear','restart':'flight','oneoff':'flight','cockpit':'cockpit','landing':'landing','safe':'landing'}
def render(lang,k,p=0,seconds=None):
 en=lang=='en';tr=lambda a,b:b if en else a;seconds=p*2 if seconds is None else seconds
 anchors={}
 if k in ['archive','volcano','evidence']:im=archive({'archive':'plane','volcano':'volcano','evidence':'blades'}[k],lang)
 else:
  kind=MAPPING[k];meta=index(kind);i=min(meta['count']-1,round(seconds*30));
  if k=='ocean':i=meta['count']-1
  im=model(kind,i).copy();anchors=meta['anchors'][i]
 d=ImageDraw.Draw(im)
 head(d,TITLES[k][en])
 if k in ['fail','alloff','question','attempt','turn','restart','oneoff']:
  active=[True]*4
  if k=='fail':
   for n in [4,2,1,3][:min(4,int(p*4.8))]:active[n-1]=False
  elif k=='restart':
   active=[False]*4
   for n in [4,3,1,2][:min(4,1+int(p*4))]:active[n-1]=True
  elif k=='oneoff':active=[True,False,True,True]
  else:active=[False]*4
  for n in range(4):
   x=210+n*220;col=GREEN if active[n] else RED
   d.rounded_rectangle((x-78,360,x+78,465),radius=18,fill=BG,outline=col,width=3);text(d,(x,392),str(n+1),36,col);text(d,(x,439),tr('ТЯГА','THRUST') if active[n] else tr('НЕТ','OFF'),26,col)
   ax,ay=anchors['engine'+str(n+1)];d.ellipse((ax-12,ay-12,ax+12,ay+12),outline=col,width=4);text(d,(ax,ay+34),str(n+1),24,col)
  if k=='attempt':
   for n in range(4):
    x=210+n*220;d.arc((x-45,510,x+45,600),int(seconds*100),int(seconds*100)+270,fill=GOLD,width=5)
   tag(d,(540,1310),tr('СНОВА И СНОВА — БЕЗ УСПЕХА','AGAIN AND AGAIN — NO RESTART'),GOLD,34)
  elif k=='restart':tag(d,(540,1310),tr('ОКОЛО 15 МИНУТ БЕЗ ТЯГИ','ABOUT 15 MINUTES WITHOUT THRUST'),GREEN,33)
  elif k=='oneoff':tag(d,(540,1310),tr('ДВИГАТЕЛЬ №2 ОТКЛЮЧЁН','ENGINE 2 SHUT DOWN'),GOLD)
  elif k=='question':text(d,(540,1300),tr('ПРИЧИНА ПОКА НЕИЗВЕСТНА','THE CAUSE IS STILL UNKNOWN'),39,GOLD)
  elif k=='turn':text(d,(540,1300),tr('НЕ ТОПЛИВО','NOT THE FUEL'),50,GOLD)
 if k=='glow':tag(d,(540,1235),tr('ГОЛУБОЕ СВЕЧЕНИЕ У СТЁКОЛ','A BLUE GLOW AT THE WINDSCREEN'),CYAN,34)
 if k=='archive':
  text(d,(65,290),'BRITISH AIRWAYS 009',32,GOLD,'lm');text(d,(540,400),tr('КУАЛА-ЛУМПУР → ПЕРТ','KUALA LUMPUR → PERTH') if p>.6 else tr('НАСТОЯЩИЙ САМОЛЁТ РЕЙСА','THE ACTUAL AIRCRAFT'),36,CYAN)
  text(d,(540,1320),tr('G-BDXH · ХИТРОУ · ЯНВАРЬ 1982','G-BDXH · HEATHROW · JANUARY 1982'),29,WHITE)
 if k=='volcano':
  text(d,(65,295),tr('ГАЛУНГГУНГ · ИНДОНЕЗИЯ','GALUNGGUNG · INDONESIA'),32,GOLD,'lm')
  text(d,(540,1320),tr('АРХИВНОЕ ФОТО · 3 ДЕКАБРЯ 1982','ARCHIVE PHOTO · 3 DECEMBER 1982'),30,WHITE)
 if k=='evidence':
  text(d,(65,295),tr('ДЕТАЛИ ДВИГАТЕЛЕЙ РЕЙСА BA009','ENGINE COMPONENTS FROM BA009'),31,GOLD,'lm')
  text(d,(540,1320),tr('МУЗЕЙНЫЙ СНИМОК · 2008','MUSEUM PHOTOGRAPH · 2008'),31,WHITE)
  if p>.45:
   # Annotation identifies the photographed components, not invented forensic traces.
   lead(d,(540,405),(260,1010),tr('ОБРАЗЦЫ ПЕПЛА В ЭКСПОЗИЦИИ','ASH SPECIMENS IN THE DISPLAY'),GOLD)
 if k=='cabin':
  x,y=anchors['vent'];layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
  for j in range(22):
   u=(j/22+seconds*.15)%1;xx=x+420*u;yy=y-240*u+25*math.sin(j*2.4);rr=20+u*55;ld.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(185,191,185,int((1-u)*65)))
  im=Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(15))).convert('RGB');d=ImageDraw.Draw(im);tag(d,(540,1300),tr('ДЫМ ПРОНИКАЕТ ВНУТРЬ','SMOKE ENTERS THE CABIN'),GOLD,35)
 if k in ['glide','ocean','escape']:
  arrow(d,(930,620),(930,620+ease(min(seconds/2,1))*500),CYAN,5)
  tag(d,(810,1260),tr('СНИЖЕНИЕ','DESCENT'),CYAN)
  if k=='ocean':
   for n in range(3):d.line([(80+x,1320+n*22+math.sin(x/45)*7) for x in range(850)],fill='#4a7e99',width=2)
  if k=='escape':
   layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer)
   for j in range(30):
    x=80+(j*131)%900;y=550+(j*71)%230-seconds*90;r=70+(j%4)*20;ld.ellipse((x-r,y-r,x+r,y+r),fill=(119,117,106,27))
   im=Image.alpha_composite(im.convert('RGBA'),layer.filter(ImageFilter.GaussianBlur(22))).convert('RGB');d=ImageDraw.Draw(im);head(d,TITLES[k][en]);tag(d,(540,390),tr('САМОЛЁТ ПОКИДАЕТ ПЕПЕЛ','THE AIRCRAFT LEAVES THE ASH'),GREEN,34)
 if k=='radar':
  c=anchors['center'];j=int(seconds*18)%72;pts=[c]+[anchors['ring'+str((j-i)%72)] for i in range(8)]
  layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer);ld.polygon(pts,fill=(65,235,125,55));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(im)
  text(d,(540,390),tr('ПОГОДНЫЙ РАДАР','WEATHER RADAR'),40,CYAN);tag(d,(540,1320),tr('СУХОЙ ПЕПЕЛ НЕ ОТОБРАЖАЕТСЯ','DRY ASH IS NOT DISPLAYED'),GOLD,35)
 if k in ['deposit','blocked','clear']:
  cols=[CYAN,GOLD,RED] if k!='clear' else [CYAN,CYAN,GREEN]
  for x,key,label,col in [(230,'compressor',tr('КОМПРЕССОР','COMPRESSOR'),CYAN),(550,'hot',tr('ГОРЯЧАЯ ЗОНА','HOT SECTION'),GOLD),(850,'turbine',tr('ТУРБИНА','TURBINE'),cols[-1])]:lead(d,(x,490),anchors[key],label,col)
  a=anchors['intake'];b=anchors['exhaust'];hot=anchors['turbine'];q=min(1,seconds/2)
  if k=='blocked':flow=.15
  elif k=='clear':flow=.15+.85*ease(q)
  else:flow=1-.8*ease(q)
  # Airflow is an explicit graphic path, not a literal flame outside the engine.
  y=1190;arrow(d,(140,y),(140+800*flow,y),CYAN,6);text(d,(540,1250),tr('ПОТОК ВОЗДУХА','AIRFLOW'),34,CYAN)
  for j in range(22):
   u=(seconds*.30+j/22)%1
   if k=='blocked' and u>.65:continue
   x=a[0]+(hot[0]-a[0])*u;yy=a[1]+(hot[1]-a[1])*u+math.sin(j*2.4)*22
   if k=='clear':x=hot[0]+u*190;yy=hot[1]+u*180
   color=GOLD if k=='deposit' else '#b9b6aa';d.ellipse((x-4,yy-4,x+4,yy+4),fill=color)
  label=tr('ПЛАВИТСЯ → НАЛИПАЕТ','MELTS → STICKS') if k=='deposit' else tr('ОТЛОЖЕНИЯ МЕШАЮТ ПОТОКУ','DEPOSITS RESTRICT FLOW') if k=='blocked' else tr('ОСТЫВАЕТ → ОТКАЛЫВАЕТСЯ','COOLS → BREAKS AWAY')
  tag(d,(540,1340),label,cols[-1],34)
 if k=='cockpit':lead(d,(540,450),anchors['glass'],tr('СТЁКЛА ПОВРЕЖДЕНЫ ПЕПЛОМ','WINDSCREENS ABRADED BY ASH'),GOLD);tag(d,(540,1310),tr('ОБЗОР РЕЗКО ОГРАНИЧЕН','VISIBILITY SEVERELY LIMITED'),GOLD,35)
 if k in ['landing','safe']:
  tag(d,(540,390),'JAKARTA · HALIM',GOLD,39)
  if k=='safe':text(d,(540,1320),tr('ВСЕ ВЫЖИЛИ','ALL SURVIVED'),60,GREEN)
 return im
