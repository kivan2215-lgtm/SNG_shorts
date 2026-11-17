from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
import math,json
import numpy as np
P=Path(__file__).parent
BG='#071923';WHITE='#f5f0e6';GOLD='#ffd078';CYAN='#87dbe3';RED='#ff8e81';GREEN='#a6dbb3'
@lru_cache(100)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=42,fill=WHITE,anchor='mm',width=920):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>25:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+12)),l,font=font(size),fill=fill,anchor=anchor)
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def tag(d,xy,s,col=GOLD,size=36):
 lines=s.split('\n');w=min(990,max(font(size).getlength(x) for x in lines)+40);h=len(lines)*(size+10)+22;x,y=xy
 d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=16,fill=BG,outline='#43636c',width=2);text(d,xy,s,size,col,width=w-28)
def arrow(d,a,b,col=GOLD,width=5):
 d.line([a,b],fill=col,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-20*math.cos(ang-.45),b[1]-20*math.sin(ang-.45)),(b[0]-20*math.cos(ang+.45),b[1]-20*math.sin(ang+.45))],fill=col)
@lru_cache(24)
def source(k):return Image.open(P/'assets'/k).convert('RGB')
def contain(im,box):
 out=Image.new('RGB',(1080,1920),BG);x,y,x1,y1=box;s=min((x1-x)/im.width,(y1-y)/im.height);im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);out.paste(im,(round((x+x1-im.width)/2),round((y+y1-im.height)/2)));return out
@lru_cache(16)
def art(sheet,i):
 im=source(f'scenes{sheet}.png');w,h=im.size;im=im.crop((i%2*w//2,i//2*h//2,(i%2+1)*w//2,(i//2+1)*h//2));return contain(im,(0,0,1080,1920))
def archive(k,box=(30,330,1050,1370)):return contain(source(k+'.jpg'),box)
@lru_cache(12)
def model(kind,i):
 f=P/'frames'/kind/f'{i:04}.jpg'
 if not f.exists():
  fs=list((P/'frames'/kind).glob('probe_*.jpg'));f=min(fs,key=lambda f:abs(int(f.stem[-4:])-i))
 return Image.open(f).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
N={
'hold':('ОН ДЕРЖАЛ КОМАНДИРА ЗА НОГИ','HE WAS HOLDING THE CAPTAIN’S LEGS'),
'outside':('СНАРУЖИ САМОЛЁТА','OUTSIDE THE AIRCRAFT'),
'height':('БОЛЬШЕ ПЯТИ КИЛОМЕТРОВ','OVER SEVENTEEN THOUSAND FEET'),
'grip':('ВТАЩИТЬ ОБРАТНО НЕ ПОЛУЧАЛОСЬ','THEY COULD NOT PULL HIM INSIDE'),
'braced':('НО ОНИ НЕ ОТПУСКАЛИ','BUT THEY WOULD NOT LET GO'),
'date':('10 ИЮНЯ 1990 · РЕЙС BA5390','10 JUNE 1990 · FLIGHT BA5390'),
'normal':('ОБЫЧНЫЙ РЕЙС В ИСПАНИЮ','A ROUTINE FLIGHT TO SPAIN'),
'blow':('ЛЕВОЕ СТЕКЛО ВЫРВАЛО НАРУЖУ','THE LEFT WINDSCREEN BLEW OUT'),
'ejected':('КОМАНДИР ОКАЗАЛСЯ СНАРУЖИ','THE CAPTAIN WAS FORCED OUT'),
'grab':('БОРТПРОВОДНИК УСПЕЛ СХВАТИТЬ ЕГО','AN ATTENDANT GRABBED HIM'),
'help':('НА ПОМОЩЬ ПРИШЛИ КОЛЛЕГИ','HIS COLLEAGUES CAME TO HELP'),
'copilot':('ВТОРОЙ ПИЛОТ УПРАВЛЯЛ САМОЛЁТОМ','THE COPILOT TOOK CONTROL'),
'airport':('НУЖЕН БЛИЖАЙШИЙ АЭРОДРОМ','FINDING THE NEAREST AIRPORT'),
'radio':('ВЕТЕР ЗАГЛУШАЛ РАДИО','WIND DROWNED OUT THE RADIO'),
'numb':('РУКИ НАЧАЛИ НЕМЕТЬ','THEIR HANDS WERE GOING NUMB'),
'believed':('ОНИ ПОЧТИ НЕ НАДЕЯЛИСЬ','THEY FEARED HE WOULD NOT SURVIVE'),
'holding':('НО ПРОДОЛЖАЛИ ДЕРЖАТЬ','BUT THEY KEPT HOLDING ON'),
'kick':('И ВДРУГ ОН ПОШЕВЕЛИЛ НОГАМИ','THEN HE KICKED HIS LEGS'),
'alive':('ОН БЫЛ ЖИВ','HE WAS ALIVE'),
'duration':('ОКОЛО ДВАДЦАТИ МИНУТ СНАРУЖИ','AROUND TWENTY MINUTES OUTSIDE'),
'landing':('ПОСАДКА В САУТГЕМПТОНЕ','LANDING AT SOUTHAMPTON'),
'survived':('ВСЕ НА БОРТУ СПАСЛИСЬ','EVERYONE ON BOARD SURVIVED'),
'why':('НО ПОЧЕМУ ВЫЛЕТЕЛО СТЕКЛО?','BUT WHY DID THE WINDOW FAIL?'),
'evidence':('НАХОДКА СЛЕДОВАТЕЛЕЙ','WHAT INVESTIGATORS FOUND'),
'repair':('ОКНО ЗАМЕНИЛИ ДО ПОЛЁТА','THE WINDOW HAD BEEN REPLACED'),
'ninety':('90 КРЕПЁЖНЫХ БОЛТОВ','90 SECURING BOLTS'),
'thin':('84 БЫЛИ ТОНЬШЕ НУЖНОГО','84 WERE TOO NARROW'),
'difference':('РАЗНИЦА — ВСЕГО 0,66 ММ','THE DIFFERENCE: JUST 0.66 MM'),
'short':('ЕЩЁ ШЕСТЬ — СЛИШКОМ КОРОТКИЕ','SIX MORE WERE TOO SHORT'),
'pressure':('ДАВЛЕНИЕ ВЫТОЛКНУЛО СТЕКЛО','CABIN PRESSURE FORCED IT OUT'),
'report':('ЧТО УСТАНОВИЛО РАССЛЕДОВАНИЕ','WHAT THE INVESTIGATION FOUND'),
'oversight':('НЕ ТОЛЬКО ОШИБКА ПРИ РЕМОНТЕ','NOT JUST A MAINTENANCE ERROR'),
'stakes':('ПОД УГРОЗОЙ — ДЕСЯТКИ ЖИЗНЕЙ','DOZENS OF LIVES AT RISK'),
'mechanic':('ВИНА ОДНОГО ЧЕЛОВЕКА?','ONE PERSON’S FAULT?'),
'end':('ИЛИ СБОЙ СИСТЕМЫ КОНТРОЛЯ?','OR A FAILURE OF OVERSIGHT?')}
def head(d,s):
 d.rounded_rectangle((65,153,131,162),radius=4,fill=GOLD);text(d,(65,213),s,42,WHITE,'lm',950)
def lowtag(d,s,col=GOLD):tag(d,(540,1398),s,col,36)
def callout(d,xy,s,target,col=GOLD,size=32):
 # Route from nearest edge of label, never through its own text.
 lines=s.split('\n');w=max(font(size).getlength(x) for x in lines)+40;h=len(lines)*(size+10)+22
 dx=target[0]-xy[0];dy=target[1]-xy[1]
 if abs(dx)/(w/2)>abs(dy)/(h/2):a=(xy[0]+math.copysign(w/2,dx),xy[1])
 else:a=(xy[0],xy[1]+math.copysign(h/2,dy))
 arrow(d,a,target,col,4);tag(d,xy,s,col,size)
def render(lang,k,p=0,seconds=None):
 tr=lambda a,b:b if lang=='en' else a;seconds=p*3 if seconds is None else seconds
 artmap={'outside':(1,0),'height':(2,0),'grip':(1,3),'braced':(3,3),'normal':(3,1),'ejected':(1,0),'grab':(1,3),'help':(1,1),'copilot':(1,2),'radio':(3,0),'numb':(1,3),'believed':(3,3),'holding':(1,1),'kick':(1,3),'alive':(1,3),'airport':(3,2),'duration':(1,0),'landing':(2,2),'repair':(2,3),'mechanic':(2,3)}
 if k=='hold':im=contain(source('opening.png'),(0,0,1080,1920))
 elif k in ['numb','kick','alive','grab']:im=contain(source({'numb':'numb.png','kick':'kick.png','alive':'kick.png','grab':'opening.png'}[k]),(0,0,1080,1920))
 elif k in artmap:im=art(*artmap[k]).copy()
 elif k=='date':im=archive('aircraft',(25,430,1055,1210))
 elif k in ['survived','stakes']:im=archive('crew',(20,390,1060,1300))
 elif k=='end':im=archive('captain',(25,350,1055,1280))
 elif k=='evidence':im=archive('appendix-19',(100,300,980,1410))
 elif k in ['report','oversight']:im=archive('report',(115,300,965,1400))
 elif k in ['blow','why','ninety','pressure']:
  i=round(min(1,seconds/1.2)*36) if k in ['blow','pressure'] else (36 if k=='why' else 0);im=model('window',i).copy()
 elif k in ['thin','difference','short']:im=model('bolts',min(60,round(seconds*30))).copy()
 else:raise ValueError(k)
 # Readability fades, not blurred duplicate imagery.
 if k=='hold' or k in artmap:
  ov=Image.new('RGBA',im.size);od=ImageDraw.Draw(ov)
  for y in range(360):
   od.line((0,y,1080,y),fill=(3,12,19,round(190*(1-y/360))))
  for y in range(1300,1920):
   od.line((0,y,1080,y),fill=(3,12,19,round(165*min(1,(y-1300)/400))))
  im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
 d=ImageDraw.Draw(im);head(d,tr(*N[k]))
 if k=='hold':lowtag(d,tr('ПОЛОВИНА ТЕЛА — ЗА БОРТОМ','HALF HIS BODY WAS OUTSIDE'))
 if k=='date':
  tag(d,(540,1260),tr('G-BJRT · ФОТО 1989 ГОДА','G-BJRT · PHOTOGRAPHED IN 1989'),CYAN,34)
  tag(d,(540,1395),tr('БИРМИНГЕМ → МАЛАГА','BIRMINGHAM → MÁLAGA'),GOLD,36)
 if k=='height':
  tag(d,(540,1380),tr('≈ 5 300 МЕТРОВ','≈ 17,300 FEET'),GOLD,48)
  # Real initial pressure altitude, no invented live speed/altimeter trace.
  text(d,(540,345),tr('ВЫСОТА В МОМЕНТ АВАРИИ','ALTITUDE AT THE WINDOW FAILURE'),30,CYAN)
 if k=='normal':lowtag(d,tr('81 ПАССАЖИР · 6 ЧЛЕНОВ ЭКИПАЖА','81 PASSENGERS · 6 CREW'),CYAN)
 if k=='ejected':lowtag(d,tr('ТИМ ЛАНКАСТЕР · КОМАНДИР','TIM LANCASTER · CAPTAIN'))
 if k=='believed':lowtag(d,tr('ХОЛОД. ВЕТЕР. НЕТ СИЛ.','COLD. WIND. EXHAUSTION.'),CYAN)
 if k=='kick':
  lowtag(d,tr('ПРИЗНАК ЖИЗНИ ПРИ СНИЖЕНИИ','A SIGN OF LIFE DURING DESCENT'))

 if k=='alive':
  lowtag(d,tr('ОН ПОДАЛ ПРИЗНАК ЖИЗНИ','HE SHOWED A SIGN OF LIFE'),GREEN)
 if k=='duration':
  tag(d,(540,1390),tr('≈ 20 МИНУТ','≈ 20 MINUTES'),GOLD,48)
 if k=='survived':
  text(d,(540,365),tr('ЭКИПАЖ В БОЛЬНИЦЕ ПОСЛЕ СПАСЕНИЯ','THE CREW IN HOSPITAL AFTER THE RESCUE'),30,CYAN)
  tag(d,(540,1340),tr('87 ЧЕЛОВЕК · 0 ПОГИБШИХ','87 PEOPLE · 0 FATALITIES'),GREEN,42)
 if k=='landing':lowtag(d,tr('ЭКИПАЖ УДЕРЖИВАЛ ЕГО ДО ПОСАДКИ','THE CREW HELD HIM THROUGH LANDING'),CYAN)
 if k=='repair':lowtag(d,tr('ЗА 27 ЧАСОВ ДО АВАРИИ','27 HOURS BEFORE THE ACCIDENT'),CYAN)
 if k in ['blow','why','ninety','pressure']:
  tag(d,(540,330),tr('УСЛОВНАЯ МОДЕЛЬ ОКНА','SCHEMATIC WINDOW MODEL'),CYAN,31)
  if k=='ninety':
   lowtag(d,tr('КРЕПЛЕНИЕ ПО ПЕРИМЕТРУ','FASTENERS AROUND THE PERIMETER'))
   callout(d,(280,480),tr('БОЛТЫ','BOLTS'),(123,973),GOLD,34)
  elif k=='pressure':
   callout(d,(270,1280),tr('ДАВЛЕНИЕ\nИЗНУТРИ','PRESSURE\nFROM INSIDE'),(470,1130),CYAN,33)
   callout(d,(800,470),tr('НАРУЖУ','OUTWARD'),(680,670),GOLD,35)
  elif k=='blow':lowtag(d,tr('ОКНО УСТАНОВЛЕНО СНАРУЖИ','THE WINDOW WAS MOUNTED FROM OUTSIDE'),CYAN)
 if k in ['thin','difference','short']:
  tag(d,(540,330),tr('УВЕЛИЧЕННОЕ СРАВНЕНИЕ','ENLARGED COMPARISON'),CYAN,31)
  # Three objects remain in the same order across both languages and all states.
  tag(d,(205,1310),tr('НУЖНЫЙ','SPECIFIED'),CYAN,29)
  tag(d,(540,1310),tr('ТОНЬШЕ','NARROWER'),RED,29)
  tag(d,(875,1310),tr('КОРОЧЕ','SHORTER'),GOLD,29)
  if k=='thin':tag(d,(540,1410),tr('84 ИЗ 90 · НЕ ТОТ ДИАМЕТР','84 OF 90 · WRONG DIAMETER'),RED,37)
  if k=='difference':
   tag(d,(540,1400),tr('ДИАМЕТР МЕНЬШЕ НА 0,66 ММ','DIAMETER SMALLER BY 0.66 MM'),RED,37)
   # Clear bracket on the central shaft; position checked in composited preflight.
   d.line((485,900,590,900),fill=RED,width=5)
   for x in [485,590]:d.line((x,885,x,915),fill=RED,width=4)
  if k=='short':tag(d,(540,1400),tr('6 ИЗ 90 · КОРОЧЕ НА 2,54 ММ','6 OF 90 · SHORTER BY 2.54 MM'),GOLD,37)
 if k=='evidence':tag(d,(540,1410),tr('СРАВНЕНИЕ ИЗ ОТЧЁТА AAIB','COMPARISON FROM THE AAIB REPORT'),CYAN,31)
 if k=='report':tag(d,(540,1410),tr('ОФИЦИАЛЬНЫЙ ОТЧЁТ · 1992','OFFICIAL REPORT · 1992'),CYAN,32)
 if k=='oversight':
  # Translation is visibly separate, not a fabricated marked-up official scan.
  tag(d,(540,1050),tr('НЕ БЫЛО НЕЗАВИСИМОЙ\nФИНАЛЬНОЙ ПРОВЕРКИ','NO INDEPENDENT\nFINAL INSPECTION'),GOLD,38)
 if k=='stakes':lowtag(d,tr('87 ЧЕЛОВЕК ЗАВИСЕЛИ ОТ КРЕПЕЖА','87 PEOPLE DEPENDED ON THOSE FASTENERS'))
 if k=='end':
  tag(d,(540,1340),tr('ЛАНКАСТЕР ПОСЛЕ ВОЗВРАЩЕНИЯ К ПОЛЁТАМ','LANCASTER AFTER RETURNING TO FLYING'),CYAN,30)
  text(d,(540,360),tr('ЧЕЛОВЕК ИЛИ СИСТЕМА?','PERSON OR SYSTEM?'),42,GOLD)
 return im
