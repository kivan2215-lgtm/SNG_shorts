from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
import math,os
P=Path(__file__).parent;BG='#182c30';CREAM='#fff0d1';GOLD='#ffcf58';RED='#ff8069';CYAN='#8addce'
@lru_cache(100)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=42,fill=CREAM,anchor='mm',width=940):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>25:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+12)),l,font=font(size),fill=fill,anchor=anchor)
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def card(d,xy,s,col=GOLD,size=40):
 # V5: omit all upper labels, including provenance and diagram section headers.
 if xy[1]<400:return
 lines=s.split('\n');w=min(990,max(font(size).getlength(l) for l in lines)+46);h=len(lines)*(size+12)+24;x,y=xy
 d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=18,fill=BG,outline=col,width=3);text(d,xy,s,size,col,width=w-32)
def arrow(d,a,b,col=GOLD):
 d.line([a,b],fill=col,width=7);q=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-22*math.cos(q-.5),b[1]-22*math.sin(q-.5)),(b[0]-22*math.cos(q+.5),b[1]-22*math.sin(q+.5))],fill=col)
@lru_cache(20)
def source(n):return Image.open(P/'assets'/n).convert('RGB')
def contain(im,box):
 out=Image.new('RGB',(1080,1920),BG);x,y,x1,y1=box;s=min((x1-x)/im.width,(y1-y)/im.height);im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);out.paste(im,(round((x+x1-im.width)/2),round((y+y1-im.height)/2)));return out
@lru_cache(16)
def art(n,i):
 im=source(f'scenes{n}.png');w,h=im.size;im=im.crop((i%2*w//2,i//2*h//2,(i%2+1)*w//2,(i//2+1)*h//2));return contain(im,(0,270,1080,1790))
@lru_cache(24)
def model(k,i):
 f=P/'frames'/k/f'{i:04}.jpg'
 if not f.exists():
  if os.getenv('RENDER_FINAL')=='1':raise FileNotFoundError(f)
  fs=list((P/'frames'/k).glob('*.jpg'));f=min(fs,key=lambda f:abs(int(f.stem)-i))
 return Image.open(f).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
HEAD={
'hook':('ПУЛЕМЁТЫ ПРОТИВ ПТИЦ','MACHINE GUNS VS BIRDS'),'bird':('ДА. ПРОТИВ ЭМУ.','YES. AGAINST EMUS.'),'awkward':('ПЛАН БЫЛ НАДЁЖНЫЙ…','A FOOLPROOF PLAN…'),
'date':('ЗАПАДНАЯ АВСТРАЛИЯ · 1932','WESTERN AUSTRALIA · 1932'),'wheat':('ПТИЦЫ ТОПТАЛИ ПОСЕВЫ','BIRDS WERE TRAMPLING CROPS'),'ask':('ФЕРМЕРЫ ПРОСЯТ ПОМОЩИ','FARMERS ASK FOR HELP'),'arrive':('ПРИЕХАЛИ ТРОЕ ВОЕННЫХ','THREE MILITARY MEN ARRIVE'),'guns':('ВОТ С ЧЕМ ПРИЕХАЛИ','WHAT THEY BROUGHT'),
'legs':('А У ПТИЦ…','AND THE BIRDS HAVE…'),'balance':('БАЛАНС СИЛ','PERFECT MATCHMAKING'),'scatter':('СТАЯ РАЗБЕГАЕТСЯ','THE FLOCK SPLITS UP'),'catch':('ОДНА ЦЕЛЬ → МНОГО ГРУПП','ONE TARGET → MANY GROUPS'),
'ambush':('ПЛАН Б: ЗАСАДА У ВОДЫ','PLAN B: AMBUSH BY THE WATER'),'flock':('СТАЯ ПРИБЛИЖАЕТСЯ','THE FLOCK APPROACHES'),'moment':('ЗВЁЗДНЫЙ ЧАС?','THEIR BIG MOMENT?'),'jam':('ПУЛЕМЁТ ЗАКЛИНИЛО','THE GUN JAMMED'),'leave':('ПТИЦЫ УШЛИ','THE BIRDS LEFT'),'error':('ТЕХНИЧЕСКИЙ ПЕРЕРЫВ','TECHNICAL DIFFICULTIES'),
'truckplan':('ПЛАН В: ДОБАВИТЬ КОЛЁСА','PLAN C: ADD WHEELS'),'chase':('ТЕПЕРЬ ТОЧНО ДОГОНЯТ?','SURELY THIS WILL WORK?'),'rough':('ТРЯСКА СОРВАЛА ПЛАН','ROUGH RIDE. FAILED PLAN.'),'escape':('ЭМУ СНОВА УХОДИТ','THE EMU GETS AWAY AGAIN'),'mobility':('ЗАКАЗАЛИ: МОБИЛЬНОСТЬ','ORDERED: MOBILITY'),'massage':('ПОЛУЧИЛИ: МАССАЖ','DELIVERED: AN ASS MASSAGE'),
'recall':('ВОЕННЫХ ОТОЗВАЛИ','THE TROOPS WERE RECALLED'),'return':('ПОТОМ ВЕРНУЛИ','THEN SENT BACK'),'unresolved':('ПРОБЛЕМА НЕ РЕШЕНА','PROBLEM NOT SOLVED'),'caveat':('ПТИЦЫ ТОЖЕ ПОГИБАЛИ','BIRDS DID DIE'),'ended':('ОПЕРАЦИЯ ЗАКОНЧИЛАСЬ','THE OPERATION ENDED'),'farmers':('ЭМУ ОСТАЛИСЬ','THE EMUS REMAINED'),'history':('«ВОЙНА С ЭМУ»','THE “EMU WAR”'),'question':('КОГДА ПОРА МЕНЯТЬ ПЛАН?','WHEN DO YOU CHANGE THE PLAN?')}
ART={'hook':(1,0),'bird':(2,0),'awkward':(2,3),'wheat':(1,1),'ask':(1,2),'arrive':(1,3),'flock':(2,1),'moment':(2,1),'jam':(2,2),'leave':(3,1),'error':(2,2),'printer':(2,2),'truckplan':(3,0),'farmers':(3,2),'history':(3,3),'question':(3,3),'indifference':(3,3)}
HEAD['balance']=('У ПТИЦ НЕТ БЮРОКРАТИИ','BIRDS DO NOT NEED PERMISSION')
HEAD['printer']=('ГОЛУБОЙ КАРТРИДЖ ГДЕ?','WHERE IS THE CYAN CARTRIDGE?')
HEAD['indifference']=('ПТИЦАМ ПОФИГ','THE BIRDS DO NOT CARE')
HEAD['massage']=('БОЕВАЯ ВИБРАЦИЯ','COMBAT VIBRATIONS')
HEAD['mobility']=('ХОТЕЛИ БОЕВУЮ МАШИНУ','THEY WANTED A FIGHTING VEHICLE')
def render(lang,k,p=0,seconds=None):
 tr=lambda a,b:b if lang=='en' else a;sec=p*3 if seconds is None else seconds
 if k in ['mobility','massage']:im=contain(source('truck_reaction.png'),(0,270,1080,1790))
 elif k in ART:im=art(*ART[k]).copy()
 elif k in ['date','guns','ambush','caveat','ended']:
  name={'date':'field','guns':'gun','ambush':'rest','caveat':'gunners','ended':'field'}[k];im=contain(source(name+'.jpg'),(40,400,1040,1270))
 elif k in ['legs','balance','scatter','catch']:
  i=min(48,round(sec*30)) if k=='scatter' else (48 if k=='catch' else 0);im=model('scatter',i).copy()
 elif k in ['chase','rough','escape','mobility','massage','recall','return','unresolved']:
  i=min(60,round(sec*30)) if k=='rough' else (0 if k=='chase' else 60);im=model('truck',i).copy()
 else:raise ValueError(k)
 if k in ART or k in ['mobility','massage']:
  overlay=Image.new('RGBA',im.size);od=ImageDraw.Draw(overlay)
  for y in range(1350,1920):od.line((0,y,1080,y),fill=(10,24,26,int(205*min(1,(y-1350)/300))))
  im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')
 d=ImageDraw.Draw(im) # V5: no top heading
 if k in ['date','guns','ambush','caveat','ended']:
  card(d,(540,330),tr('ПОДЛИННЫЙ СНИМОК · 1932','ARCHIVAL PHOTOGRAPH · 1932'),CYAN,32)
 if k=='date':card(d,(540,1310),tr('ПОСЕВЫ И ОГРАЖДЕНИЯ','CROPS AND FENCES'),GOLD,38)
 if k=='guns':
  card(d,(540,1320),tr('2 ПУЛЕМЁТА  •  10 000 ПАТРОНОВ','2 GUNS  •  10,000 ROUNDS'),GOLD,39)
 if k in ['legs','balance']:
  card(d,(540,325),tr('СОЛДАТЫ: ОРУЖИЕ И ПАТРОНЫ','SOLDIERS: GUNS AND AMMUNITION'),GOLD,38)
  card(d,(540,1320),tr('ЭМУ: НОГИ','EMUS: LEGS'),CYAN,50)
  if k=='balance':
   # Editorial comparison, not a claim about military victory or kill totals.
   text(d,(540,1420),tr('БЕЗ СОГЛАСОВАНИЙ','NO APPROVAL REQUIRED'),38,GOLD)
 if k in ['scatter','catch']:
  card(d,(540,300),tr('УСЛОВНАЯ СХЕМА ДВИЖЕНИЯ','SCHEMATIC MOVEMENT'),CYAN,32)
  u=ease(sec/1.6) if k=='scatter' else 1
  for a,b in [((480,1000),(240,1040)),((535,970),(600,735)),((585,1030),(835,1090))]:
   end=(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
   if u>.05:arrow(d,a,end,CYAN)
  card(d,(540,1350),tr('ГРУППЫ УХОДЯТ В РАЗНЫЕ СТОРОНЫ','GROUPS RUN IN DIFFERENT DIRECTIONS'),CYAN,34)
 if k=='moment':card(d,(540,1290),tr('ЧТО МОЖЕТ ПОЙТИ НЕ ТАК?','WHAT COULD POSSIBLY GO WRONG?'),GOLD,39)
 if k=='jam':card(d,(540,1290),tr('ЗАКЛИНИЛО','JAMMED'),RED,55)
 if k in ['error','printer']:
  # Explicitly a comedy UI metaphor, no invented historical computer or document.
  x,y=140,1190;d.rounded_rectangle((x,y,940,y+210),radius=25,fill=BG,outline=RED,width=4)
  text(d,(540,y+55),(tr('КАРТРИДЖ НЕ НАЙДЕН','CYAN CARTRIDGE MISSING') if k=='printer' else tr('ИНТЕЛЛЕКТ: ПЕРЕЗАГРУЗКА','INTELLIGENCE: REBOOTING')),36,RED)
  d.rounded_rectangle((190,y+115,890,y+155),radius=16,fill='#304341');d.rounded_rectangle((190,y+115,190+round(650*min(.13,sec*.05)),y+155),radius=16,fill=GOLD)
  text(d,(540,y+190),tr('ПОЖАЛУЙСТА, ПОДОЖДИТЕ','PLEASE STAND BY'),28,CREAM)
 if k in ['chase','rough','escape']:
  card(d,(540,300),tr('НОВЫЙ ПЛАН: ДОГНАТЬ ПТИЦ','NEW PLAN: CHASE THE BIRDS'),CYAN,32)
  if k=='rough':
   card(d,(540,1320),tr('ТРЯСКА МЕШАЕТ СТРЕЛЬБЕ','BOUNCING PREVENTS ACCURATE FIRE'),RED,38)
  elif k=='escape':card(d,(540,1320),tr('ПТИЦА ПО-ПРЕЖНЕМУ ВПЕРЕДИ','THE BIRD IS STILL AHEAD'),CYAN,38)
  elif k in ['mobility','massage']:pass
 if k in ['recall','return','unresolved']:
  card(d,(540,300),tr('ЭТАПЫ ОПЕРАЦИИ · НОЯБРЬ 1932','OPERATION STAGES · NOVEMBER 1932'),CYAN,33)
  a=(240,1300);b=(840,1300);u=ease(sec/1.0)
  card(d,(240,1175),tr('ОТОЗВАЛИ','RECALLED'),CREAM,34)
  if k!='recall':card(d,(840,1175),tr('ВЕРНУЛИ','RETURNED'),CREAM,34)
  if k=='recall':card(d,(240,1300),tr('8 НОЯБРЯ','NOV 8'),GOLD,38)
  else:
   arrow(d,a,(a[0]+(b[0]-a[0])*u,b[1]),GOLD);card(d,(240,1300),tr('8 НОЯБРЯ','NOV 8'),CREAM,38);card(d,(840,1300),tr('13 НОЯБРЯ','NOV 13'),GOLD,38)
  if k=='unresolved':card(d,(540,1410),tr('ЭМУ НИКУДА НЕ ДЕЛИСЬ','THE EMUS WERE STILL THERE'),RED,35)
 if k=='ended':card(d,(540,1320),tr('ДЕКАБРЬ 1932: ВОЕННЫЙ ЭТАП ЗАКОНЧЕН','DECEMBER 1932: MILITARY PHASE ENDS'),CYAN,35)
 if k=='question':
  card(d,(540,1320),tr('УПОРСТВО ИЛИ УПРЯМСТВО?','PERSISTENCE OR STUBBORNNESS?'),GOLD,40)
 return im
