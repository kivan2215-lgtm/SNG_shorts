from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
import math,json
P=Path(__file__).parent
BG='#071923';WHITE='#f5f0e6';GOLD='#ffd078';CYAN='#87dbe3';RED='#ff8e81';GREEN='#a6dbb3'
@lru_cache(100)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=42,fill=WHITE,anchor='mm',width=920):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>24:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+12)),l,font=font(size),fill=fill,anchor=anchor)
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def tag(d,xy,s,col=GOLD,size=34):
 lines=s.split('\n');w=min(990,max(font(size).getlength(x) for x in lines)+36);h=len(lines)*(size+10)+20;x,y=xy
 d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=16,fill=BG,outline='#43636c',width=2);text(d,xy,s,size,col,width=w-28)
def arrow(d,a,b,col=GOLD,width=5):
 d.line([a,b],fill=col,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-20*math.cos(ang-.45),b[1]-20*math.sin(ang-.45)),(b[0]-20*math.cos(ang+.45),b[1]-20*math.sin(ang+.45))],fill=col)
@lru_cache(12)
def art(sheet,index):
 src=P/'assets'/f'scenes{sheet}.png'
 if sheet==3 and index==0 and (P/'assets/scenes3_fixed.png').exists():src=P/'assets/scenes3_fixed.png'
 im=Image.open(src).convert('RGB');w,h=im.size;im=im.crop((index%2*w//2,index//2*h//2,(index%2+1)*w//2,(index//2+1)*h//2));im.thumbnail((1080,1440),Image.Resampling.LANCZOS)
 scale=min(1080/im.width,1440/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 out=Image.new('RGB',(1080,1920),BG);out.paste(im,((1080-im.width)//2,250+(1440-im.height)//2));overlay=Image.new('RGBA',out.size);d=ImageDraw.Draw(overlay)
 for y in range(200):d.line((0,250+y,1080,250+y),fill=(7,25,35,round(110*(1-y/200))))
 for y in range(250):d.line((0,1440+y,1080,1440+y),fill=(7,25,35,round(200*y/250)))
 return Image.alpha_composite(out.convert('RGBA'),overlay).convert('RGB')
@lru_cache(70)
def model(k,i=0):return Image.open(P/'frames'/k/f'{i:04d}.jpg').convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
@lru_cache(6)
def photo(k):return Image.open(P/'assets'/f'{k}.jpg').convert('RGB')
def archive(k,box=(70,430,1010,1380)):
 out=Image.new('RGB',(1080,1920),BG);pic=photo(k).copy();x,y,x1,y1=box;pic.thumbnail((x1-x,y1-y),Image.Resampling.LANCZOS);out.paste(pic,(int((x+x1-pic.width)/2),int((y+y1-pic.height)/2)));return out
N={
'fall':('ОТКАЗАЛ ПАРАШЮТ','HER PARACHUTE FAILED'),
'reserve':('ОСТАВАЛСЯ ЗАПАСНОЙ','SHE HAD A RESERVE'),
'failed':('ОН ТОЖЕ НЕ СПАСАЛ','THAT FAILED TOO'),
'height':('БОЛЬШЕ КИЛОМЕТРА ДО ЗЕМЛИ','OVER A KILOMETER TO THE GROUND'),
'hook':('СТРАШНЕЕ ОКАЗАЛАСЬ ПРАВДА','THE TRUTH WAS MORE TERRIFYING'),
'date':('АНГЛИЯ · 5 АПРЕЛЯ 2015','ENGLAND · 5 APRIL 2015'),
'victoria':('ВИКТОРИЯ СИЛЬЕРС','VICTORIA CILLIERS'),
'gift':('ПРЫЖОК ПОСЛЕ РОЖДЕНИЯ РЕБЁНКА','A JUMP AFTER HER CHILD’S BIRTH'),
'field':('ОНА УПАЛА НА ВСПАХАННОЕ ПОЛЕ','SHE LANDED IN A PLOUGHED FIELD'),
'rescue':('ТЯЖЕЛЕЙШИЕ ТРАВМЫ','DEVASTATING INJURIES'),
'alive':('НО ОНА ВЫЖИЛА','BUT SHE SURVIVED'),
'accident':('НЕСЧАСТНЫЙ СЛУЧАЙ?','AN ACCIDENT?'),
'evidence':('СНАРЯЖЕНИЕ СТАЛО УЛИКОЙ','THE EQUIPMENT BECAME EVIDENCE'),
'both':('ДВА ПАРАШЮТА БЫЛИ ПОВРЕЖДЕНЫ','BOTH PARACHUTES WERE SABOTAGED'),
'strange':('НО БЫЛО ЕЩЁ ОДНО СОБЫТИЕ','BUT THERE WAS ANOTHER EVENT'),
'gas':('ЗА НЕДЕЛЮ ДО ПРЫЖКА','ONE WEEK BEFORE THE JUMP'),
'linked':('ДВА СОБЫТИЯ СВЯЗАЛИ','INVESTIGATORS CONNECTED THEM'),
'attempt':('ЭТО БЫЛА НЕ ПЕРВАЯ ПОПЫТКА','THIS WAS NOT THE FIRST ATTEMPT'),
'question':('КТО МОГ ПОДОБРАТЬСЯ ТАК БЛИЗКО?','WHO COULD GET THAT CLOSE?'),
'truth':('ОТВЕТ БЫЛ СОВСЕМ РЯДОМ','THE ANSWER WAS CLOSE TO HOME'),
'husband':('ЕЁ СОБСТВЕННЫЙ МУЖ','HER OWN HUSBAND'),
'emile':('ЭМИЛЬ СИЛЬЕРС','EMILE CILLIERS'),
'arranged':('ОН ОРГАНИЗОВАЛ ПРЫЖОК','HE ARRANGED THE JUMP'),
'sabotage':('ОН ЖЕ ИСПОРТИЛ СНАРЯЖЕНИЕ','HE SABOTAGED THE EQUIPMENT'),
'motive':('МОТИВ, УСТАНОВЛЕННЫЙ СУДОМ','THE MOTIVE ESTABLISHED AT TRIAL'),
'insurance':('СТРАХОВКА → ПОГАШЕНИЕ ДОЛГОВ','INSURANCE → CLEARING HIS DEBTS'),
'verdict':('2018 · ПОЖИЗНЕННОЕ ЗАКЛЮЧЕНИЕ','2018 · LIFE SENTENCE'),
'minimum':('МИНИМУМ 18 ЛЕТ','A MINIMUM OF 18 YEARS'),
'survived':('ВИКТОРИЯ ВЫЖИЛА','VICTORIA SURVIVED'),
'betrayal':('ДВА ПОКУШЕНИЯ. ОДИН ЧЕЛОВЕК.','TWO ATTEMPTS. ONE MAN.'),
'end':('ЧТО СТРАШНЕЕ?','WHICH IS MORE FRIGHTENING?')}
def head(d,s):
 d.rounded_rectangle((65,154,130,162),radius=4,fill=GOLD);text(d,(65,210),s,43,WHITE,'lm',950)
def flow(d,seconds,tr,mode):
 # Clear causal sequence, with no invented amounts, transactions or evidence.
 y=1060
 for i,(label,col) in enumerate([(tr('УТЕЧКА ГАЗА','GAS LEAK'),RED),(tr('ПРЫЖОК','SKYDIVE'),GOLD)]):
  x=280+520*i;d.rounded_rectangle((x-190,y-65,x+190,y+65),radius=18,fill=BG,outline=col,width=3);text(d,(x,y),label,34,col,width=350)
 q=ease(seconds/1.2);arrow(d,(475,y),(475+130*q,y),GOLD)
 tag(d,(540,1220),tr('ИНТЕРВАЛ — ОДНА НЕДЕЛЯ','ONE WEEK APART'),CYAN,33)
 if mode=='attempt':tag(d,(540,1340),tr('ДВЕ ПОПЫТКИ УБИЙСТВА','TWO ATTEMPTS TO KILL HER'),RED,34)
def render(lang,k,p=0,seconds=None):
 tr=lambda a,b:b if lang=='en' else a;seconds=p*2 if seconds is None else seconds
 people={'fall':(1,0),'reserve':(3,0),'hook':(3,1),'date':(1,2),'gift':(1,1),'field':(1,3),'rescue':(2,3),'accident':(2,0),'strange':(2,1),'question':(3,2),'truth':(2,2),'verdict':(2,2),'minimum':(2,2)}
 if k in people:im=art(*people[k]).copy()
 elif k in ['height','field']:im=model('descent',min(60,round(seconds*30))).copy()
 elif k in ['gas','linked','attempt']:im=model('house').copy()
 elif k in ['victoria','alive','survived','end']:im=archive('victoria',(100,320,980,1420))
 elif k in ['husband','betrayal']:im=archive('couple',(40,370,1040,1150))
 elif k in ['emile','motive','insurance']:im=archive('emile',(40,370,1040,1050))
 elif k in ['reserve','failed','evidence','both','sabotage']:im=archive('parachute',(40,380,1040,1130))
 elif k=='arranged':im=art(1,1).copy()
 else:im=Image.new('RGB',(1080,1920),BG)
 d=ImageDraw.Draw(im);head(d,tr(*N[k]))
 if k in ['failed','both']:
  for i,label in enumerate([tr('ОСНОВНОЙ','MAIN'),tr('ЗАПАСНОЙ','RESERVE')]):
   x=290+500*i;tag(d,(x,1160),label,CYAN,34)
   bad=(i==0 or k in ['failed','both']);text(d,(x,1280),tr('ОТКАЗ','FAILED') if bad else '?',48,RED if bad else GOLD)
  arrow(d,(500,1160),(575,1160),GOLD)
 if k=='height':
  tag(d,(540,1250),tr('ОКОЛО 1200 МЕТРОВ','ABOUT 1,200 METERS'),GOLD,40)
  tag(d,(540,1360),tr('СХЕМА СПУСКА · НЕ В МАСШТАБЕ','DESCENT DIAGRAM · NOT TO SCALE'),CYAN,27)
 if k=='field':tag(d,(540,430),tr('МЯГКОЕ ВСПАХАННОЕ ПОЛЕ','A SOFT, PLOUGHED FIELD'),GOLD,36)
 if k=='victoria':tag(d,(540,1390),tr('ОПЫТНЫЙ ИНСТРУКТОР','EXPERIENCED INSTRUCTOR'),CYAN,36)
 if k=='evidence':tag(d,(540,1230),tr('ПОЛИЦИЯ ОСМОТРЕЛА СНАРЯЖЕНИЕ','POLICE EXAMINED THE EQUIPMENT'),CYAN,33)
 if k=='gas':
  tag(d,(540,420),tr('УТЕЧКА ГАЗА В ЕЁ ДОМЕ','A GAS LEAK AT HER HOME'),RED,37)
  tag(d,(540,1320),tr('ДО ПРЫЖКА ОСТАВАЛАСЬ НЕДЕЛЯ','A WEEK BEFORE THE JUMP'),GOLD,34)
 if k in ['linked','attempt']:
  # Move model upward as a complete inset, then connect events below it.
  pic=model('house').resize((750,1333),Image.Resampling.LANCZOS);im=Image.new('RGB',(1080,1920),BG);im.paste(pic,(165,-120));d=ImageDraw.Draw(im);head(d,tr(*N[k]));flow(d,seconds,tr,k)
 if k=='reserve':tag(d,(540,1340),tr('ПОПЫТКА РАСКРЫТЬ ЗАПАСНОЙ','DEPLOYING THE RESERVE'),CYAN,32)
 if k=='emile':tag(d,(540,1190),tr('ВОЕННОСЛУЖАЩИЙ · МУЖ ВИКТОРИИ','ARMY SERGEANT · VICTORIA’S HUSBAND'),GOLD,32)
 if k=='arranged':tag(d,(540,1350),tr('ПРЫЖОК ОРГАНИЗОВАЛ МУЖ','HER HUSBAND ARRANGED IT'),GOLD,33)
 if k=='sabotage':tag(d,(540,1220),tr('УМЫШЛЕННОЕ ВМЕШАТЕЛЬСТВО','DELIBERATE SABOTAGE'),RED,38)
 if k=='motive':
  tag(d,(540,1130),tr('НОВАЯ ЖИЗНЬ С ЛЮБОВНИЦЕЙ','A NEW LIFE WITH A LOVER'),GOLD,35)
  tag(d,(540,1280),tr('ИЗБАВИТЬСЯ ОТ ДОЛГОВ','CLEARING HIS DEBTS'),CYAN,35)
 if k=='insurance':
  tag(d,(540,1080),tr('СМЕРТЬ ЖЕНЫ','HIS WIFE’S DEATH'),RED,35)
  arrow(d,(540,1120),(540,1190),GOLD);tag(d,(540,1240),tr('СТРАХОВАЯ ВЫПЛАТА','INSURANCE PAYOUT'),GOLD,35)
  if seconds>.7:tag(d,(540,1370),tr('ПОГАШЕНИЕ ДОЛГОВ','DEBTS PAID OFF'),CYAN,34)
 if k=='minimum':tag(d,(540,1320),tr('18 ЛЕТ — НЕ ДАТА ОСВОБОЖДЕНИЯ','18 YEARS IS NOT A RELEASE DATE'),GOLD,32)
 if k=='betrayal':
  tag(d,(540,1110),tr('ДОМА — ГАЗ','AT HOME: GAS'),RED,35);tag(d,(540,1260),tr('В НЕБЕ — ДВА ПАРАШЮТА','IN THE SKY: BOTH PARACHUTES'),RED,35)
 if k=='end':tag(d,(540,1380),tr('ПАДЕНИЕ ИЛИ ПРЕДАТЕЛЬСТВО?','THE FALL OR THE BETRAYAL?'),GOLD,35)
 return im
