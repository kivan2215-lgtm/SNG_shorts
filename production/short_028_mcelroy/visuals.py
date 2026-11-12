from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
from functools import lru_cache
import math
A=Path(__file__).parent/'assets'
BG='#101d29';INK='#f2eee3';GOLD='#ebbd6a';TEAL='#7dc6c6';RED='#d58b78';MUTED='#a5b7bf'
@lru_cache(120)
def font(n,bold=True):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
def txt(d,xy,s,n=46,c=INK,w=930):
 while max(font(n).getlength(z) for z in s.split('\n'))>w:n-=1
 d.multiline_text(xy,s,font=font(n),fill=c,anchor='mm',align='center',spacing=16)
def base(title,kicker=''):
 im=Image.new('RGB',(1080,1920),BG);d=ImageDraw.Draw(im)
 for y in range(1920):
  f=max(0,1-abs(y-850)/1050);d.line((0,y,1080,y),fill=(int(13+7*f),int(25+11*f),int(37+13*f)))
 d.line((70,133,190,133),fill=GOLD,width=5)
 if kicker:txt(d,(540,135),kicker,26,MUTED)
 txt(d,(540,245),title,54)
 d.line((70,1725,1010,1725),fill='#2e4554',width=2)
 return im
@lru_cache(40)
def load(name):return Image.open(A/(name+'.jpg')).convert('RGB')
def photo(name,title,detail='',badge=''):
 im=base(title);pic=ImageOps.contain(load(name),(1080,1050),Image.Resampling.LANCZOS);y=370+(1050-pic.height)//2;im.paste(pic,((1080-pic.width)//2,y));d=ImageDraw.Draw(im)
 if detail:txt(d,(540,1355),detail,35,GOLD)
 if badge:txt(d,(540,430),badge,36,GOLD)
 return im
def panel(d,box,title,detail='',color=TEAL):
 x,y,w,h=box;d.rounded_rectangle((x,y,x+w,y+h),radius=22,fill='#203746',outline='#48616e',width=2);d.rounded_rectangle((x,y,x+8,y+h),radius=3,fill=color)
 txt(d,(x+w/2,y+h*.36),title,42,color,w=w-50)
 if detail:txt(d,(x+w/2,y+h*.72),detail,31,INK,w=w-50)
def person(d,x,y,col=GOLD,scale=1):
 r=int(12*scale);d.ellipse((x-r,y-r,x+r,y+r),fill=col);d.rounded_rectangle((x-17*scale,y+17*scale,x+17*scale,y+65*scale),int(7*scale),fill=col)
def truck(d,x,y,scale=1):
 def b(a):return tuple(int(v*scale+(x if i%2==0 else y)) for i,v in enumerate(a))
 d.rounded_rectangle(b((-120,-65,120,65)),15,fill='#9d5145',outline='#e3c2a1',width=3)
 d.rectangle(b((-30,-53,25,53)),fill='#718a94');d.rectangle(b((36,-50,105,50)),fill='#543b37',outline='#c69a83',width=3)
 for yy in [-72,55]:
  for xx in [-85,70]:d.rounded_rectangle(b((xx,yy,xx+30,yy+17)),5,fill='#081019')
 d.line(b((-103,-45,-103,45)),fill='#efcf97',width=4)
def route(d,points,p=1,color=GOLD):
 lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];travel=sum(lengths)*max(0,min(1,p));left=travel
 for a,b,l in zip(points,points[1:],lengths):
  if left<=0:break
  q=min(1,left/l);end=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);d.line((a,end),fill=color,width=7);left-=l
  if q<1:break
 if travel>0:d.ellipse((end[0]-10,end[1]-10,end[0]+10,end[1]+10),fill=INK)
def store(d,T,survived=False):
 d.polygon([(150,610),(930,610),(880,440),(200,440)],fill='#776a58');d.rectangle((175,610,905,1120),fill='#b6a68a',outline='#e2d6be',width=4)
 d.rectangle((215,660,555,980),fill='#213844');d.rectangle((620,660,845,1120),fill='#3b5158',outline='#f0e2c8',width=4);d.rectangle((650,700,810,950),fill='#1c2f3a');d.ellipse((817,993,827,1003),fill=GOLD)
 for x in range(235,535,65):
  for y in [750,835,915]:d.rectangle((x,y,x+38,y+45),fill='#7f9289')
 d.rectangle((205,520,875,600),fill='#203541');txt(d,(540,560),T('ПРОДУКТОВЫЙ МАГАЗИН','GROCERY STORE'),35)
 txt(d,(540,1205),T('ПОСТРАДАВШИЙ — ВЛАДЕЛЕЦ','THE OWNER WAS SHOT'),39,GOLD)
 if survived:panel(d,(130,1270,820,140),T('ОН ВЫЖИЛ','HE SURVIVED'),'',TEAL)
@lru_cache(3)
def illustrated_panel(i):
 sheet=Image.open(A/'illustrations.png').convert('RGB');w,h=sheet.size
 return sheet.crop((i*w//3+5,0,(i+1)*w//3-5,h))
def illustration(i,title,detail=''):
 im=base(title);pic=ImageOps.fit(illustrated_panel(i),(1080,1100),Image.Resampling.LANCZOS);im.paste(pic,(0,340))
 if detail:
  d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1300,1080,1440),fill=(10,22,31,210));txt(d,(540,1360),detail,43,GOLD)
 return im
def render(lang,kind,p=1):
 T=lambda a,b:a if lang=='ru' else b
 if kind=='store':return illustration(0,T('ВЫСТРЕЛ В ВЛАДЕЛЬЦА МАГАЗИНА','THE GROCER WAS SHOT'))
 if kind=='survived':return illustration(0,T('ПОСТРАДАВШИЙ ВЫЖИЛ','THE VICTIM SURVIVED'))
 if kind=='meeting':return illustration(1,T('10 ИЮЛЯ 1981','10 JULY 1981'),T('КАК ЗАЩИТИТЬСЯ?','HOW DO WE STAY SAFE?'))
 if kind=='pickup':return illustration(2,T('ОН СЕЛ В ПИКАП С ЖЕНОЙ','HE GOT IN WITH HIS WIFE'),T('ВОКРУГ СТОЯЛИ ЛЮДИ','PEOPLE STOOD AROUND THEM'))
 if kind=='opening':return photo('scene',T('ДЕСЯТКИ СВИДЕТЕЛЕЙ','DOZENS OF WITNESSES'),T('10 июля 1981 • Скидмор','10 July 1981 • Skidmore'))
 if kind=='portrait':return photo('portrait',T('КЕН РЕКС МАКЭЛРОЙ','KEN REX McELROY'),T('Его боялись в Скидморе','He was feared in Skidmore'))
 if kind=='history':return photo('ken_full',T('ГОДЫ УГРОЗ И ЗАПУГИВАНИЯ','YEARS OF THREATS'),T('Свидетели отказывались от показаний','Witnesses backed away from testifying'))
 if kind=='tavern':return photo('tavern',T('БАР D&G','THE D&G TAVERN'),T('Он снова пришёл с оружием','He returned with a gun'))
 if kind=='death':return photo('scene',T('ВЫСТРЕЛЫ СРЕДИ БЕЛА ДНЯ','SHOTS IN BROAD DAYLIGHT'),T('Подлинный снимок места убийства','The actual crime-scene photograph'))
 if kind=='wife':return photo('trena',T('ЖЕНА НАЗВАЛА СТРЕЛЯВШЕГО','HIS WIFE IDENTIFIED A GUNMAN'),T('Её показания не привели к обвинению','Her account did not lead to charges'))
 if kind=='later':return photo('town',T('ПРОШЛИ ДЕСЯТИЛЕТИЯ','DECADES PASSED'),T('Скидмор • фотография 2025 года','Skidmore • photographed in 2025'))
 if kind=='fear':return photo('ken_dog',T('КОГДА ЗАКОН НЕ ЗАЩИТИЛ','WHEN THE LAW FAILED TO PROTECT'))
 titles={'witnesses':T('СТРЕЛЯВШЕГО «НЕ ВИДЕЛИ»','THEY HAD NOT SEEN THE SHOOTER'),'location':T('СКИДМОР • МИССУРИ','SKIDMORE • MISSOURI'),'store':T('ВЫСТРЕЛ В ВЛАДЕЛЬЦА МАГАЗИНА','THE GROCER WAS SHOT'),'survived':T('ПОСТРАДАВШИЙ ВЫЖИЛ','THE VICTIM SURVIVED'),'verdict':T('НА ЭТОТ РАЗ — ВИНОВЕН','THIS TIME: CONVICTED'),'bail':T('НО ОН СНОВА НА СВОБОДЕ','BUT HE WAS FREE AGAIN'),'threats':T('НОВЫЕ УГРОЗЫ','MORE THREATS'),'meeting':T('10 ИЮЛЯ 1981','10 JULY 1981'),'arrival':T('МАКЭЛРОЙ ПРИЕХАЛ К БАРУ','McELROY ARRIVED AT THE BAR'),'move':T('ЛЮДИ НАПРАВИЛИСЬ ТУДА ЖЕ','THE CROWD HEADED TO THE BAR'),'pickup':T('ОН СЕЛ В ПИКАП С ЖЕНОЙ','HE GOT IN WITH HIS WIFE'),'accounts':T('ДВЕ РАЗНЫЕ ВЕРСИИ','CONFLICTING ACCOUNTS'),'investigation':T('РАССЛЕДОВАЛО ДАЖЕ ФБР','EVEN THE FBI INVESTIGATED'),'nocharges':T('ОБВИНЕНИЙ НЕ ПРЕДЪЯВИЛИ','NO CHARGES WERE FILED'),'law':T('ЗАКОН СНОВА БЕССИЛЕН','THE LAW WAS POWERLESS AGAIN'),'silent':T('ТЕПЕРЬ МОЛЧАЛ ГОРОД','NOW THE TOWN WAS SILENT'),'question':T('СПРАВЕДЛИВОСТЬ?','JUSTICE?'),'ending':T('ИЛИ БЕЗНАКАЗАННОЕ УБИЙСТВО?','OR MURDER WITHOUT ACCOUNTABILITY?')}
 im=base(titles[kind]);d=ImageDraw.Draw(im)
 if kind=='witnesses':
  truck(d,540,820,1.6)
  for i in range(18):
   a=2*math.pi*i/18;x=540+350*math.cos(a);y=810+290*math.sin(a);person(d,x,y,MUTED,.9)
  panel(d,(110,1230,860,180),T('ПОЧТИ ВСЕ ОТРИЦАЛИ, ЧТО ВИДЕЛИ','ALMOST ALL DENIED SEEING'),T('Кто именно стрелял','Who had fired'),GOLD)
 elif kind=='location':
  txt(d,(540,500),'1981',180,GOLD)
  # Geographic locator is deliberately a regional label, not an invented map.
  for i,(a,b) in enumerate([(T('США','UNITED STATES'),T('Центральная часть страны','The central United States')),(T('МИССУРИ','MISSOURI'),T('Северо-запад штата','Northwestern Missouri')),(T('СКИДМОР','SKIDMORE'),T('Небольшой сельский город','A small farming community'))]):
   if p>=i*.2:panel(d,(120,690+i*230,840,180),a,b,GOLD if i==2 else TEAL)
 elif kind in ['store','survived']:store(d,T,kind=='survived')
 elif kind in ['verdict','bail']:
  # Explain the legal distinction; no forged court document.
  d.polygon([(190,590),(540,410),(890,590)],fill='#9c8f77',outline='#d6c7aa');d.rectangle((180,590,900,640),fill='#c0b197')
  for x in [240,410,580,750]:d.rectangle((x,640,x+80,880),fill='#aa9e88');d.rectangle((x-12,640,x+92,668),fill='#d3c7b1');d.rectangle((x-12,855,x+92,880),fill='#d3c7b1')
  d.rectangle((170,880,910,930),fill='#d2c2a4')
  panel(d,(100,1010,880,170),T('ПРИГОВОР ЗА НАПАДЕНИЕ','CONVICTED OF ASSAULT'),T('Суд признал вину','A jury found him guilty'),GOLD)
  if kind=='bail' and p>.16:
   route(d,[(540,1185),(540,1230)],min(1,p*2));panel(d,(100,1240,880,180),T('ЗАЛОГ НА ВРЕМЯ АПЕЛЛЯЦИИ','BOND WHILE APPEALING'),T('Это не оправдание','This was not an acquittal'),RED)
 elif kind=='threats':
  pic=ImageOps.contain(load('portrait'),(430,470));im.paste(pic,(65,500));d=ImageDraw.Draw(im)
  panel(d,(570,500,440,430),T('ВЛАДЕЛЕЦ\nМАГАЗИНА','THE\nGROCER'),T('Уже пережил\nнападение','Had survived\nthe shooting'),TEAL)
  route(d,[(320,1020),(320,1150),(780,1150),(780,970)],min(1,p*1.7),RED)
  txt(d,(540,1310),T('УГРОЗЫ ПРОДОЛЖИЛИСЬ','THE THREATS CONTINUED'),42,RED)
 elif kind in ['meeting','arrival','move','pickup']:
  if kind=='pickup':
   d.rounded_rectangle((105,410,975,1280),45,fill='#39434a',outline='#687c86',width=4)
   for yy in range(450,1280,130):d.line((540,yy,540,yy+65),fill='#a49571',width=5)
   truck(d,540,825,2.6);person(d,500,790,GOLD,.85);person(d,500,860,TEAL,.85)
   txt(d,(290,600),T('КЕН','KEN'),36,GOLD);route(d,[(310,635),(445,750)],1,GOLD)
   txt(d,(790,1100),T('ЖЕНА','WIFE'),36,TEAL);route(d,[(775,1065),(560,915)],1,TEAL)
   txt(d,(540,1370),T('ВОКРУГ — ЛЮДИ','PEOPLE STOOD AROUND THEM'),40)
  else:
   # Flow diagram, not a scale site plan or shooter location.
   d.rounded_rectangle((90,410,990,740),22,fill='#294250',outline='#708996',width=3)
   d.polygon([(170,500),(410,420),(650,500)],fill='#9f957f');d.rectangle((180,500,640,650),fill='#a3957c')
   for x in range(210,620,85):d.rectangle((x,535,x+50,605),fill='#34454c')
   for i in range(5):person(d,260+i*110,665,TEAL,.7)
   txt(d,(540,795),T('СОБРАНИЕ: КАК ЗАЩИТИТЬСЯ?','MEETING: HOW DO WE STAY SAFE?'),38,TEAL)
   if kind in ['arrival','move']:
    route(d,[(540,850),(540,975)],min(1,p*2),GOLD)
    d.rounded_rectangle((110,1010,970,1335),18,fill='#5b5f57',outline='#adac94',width=3);d.rectangle((150,1040,930,1115),fill='#c0b395');txt(d,(540,1076),'D&G TAVERN',44,BG)
    d.rectangle((720,1150,870,1335),fill='#1f3039');d.rectangle((190,1150,620,1295),fill='#8d9a94')
    if kind=='move':
     for i in range(6):person(d,280+i*95,1370,GOLD,.6)
    else:truck(d,430,1370,.6)
 elif kind=='accounts':
  for i in range(9):person(d,170+i*90,475,MUTED,.8)
  panel(d,(95,680,890,270),T('ЖЕНА: УЗНАЛА СТРЕЛЯВШЕГО','WIFE: RECOGNIZED A GUNMAN'),T('Это её свидетельство','Her witness account'),GOLD)
  if p>.15:panel(d,(95,1030,890,270),T('ДРУГИЕ: НЕ ВИДЕЛИ','OTHERS: DID NOT SEE'),T('Кто произвёл выстрелы','Who fired the shots'),TEAL)
 elif kind=='investigation':
  txt(d,(540,460),'FBI',170,TEAL)
  d.rounded_rectangle((85,650,995,1310),20,fill='#e0d6bc');txt(d,(540,745),'THE WASHINGTON POST',43,BG)
  txt(d,(540,835),T('11 НОЯБРЯ 1982','11 NOVEMBER 1982'),29,'#59616a')
  d.line((140,895,940,895),fill='#8b8a7d',width=2)
  txt(d,(540,1035),'“No charges will be filed”',43,BG)
  txt(d,(540,1185),T('«Обвинения предъявлены не будут»','Report on the investigation’s outcome'),33,'#4d5e65',w=800)
 elif kind=='nocharges':
  for i,(a,b) in enumerate([(T('МЕСТНОЕ РАССЛЕДОВАНИЕ','LOCAL INVESTIGATION'),T('Не привело к обвинению','No charges')),(T('ФЕДЕРАЛЬНОЕ РАССЛЕДОВАНИЕ','FEDERAL INVESTIGATION'),T('Также без обвинений','No charges either'))]):panel(d,(100,460+i*340,880,230),a,b,TEAL)
  txt(d,(540,1260),T('ДЕЛО НЕ РАСКРЫТО','CASE UNSOLVED'),70,GOLD)
 elif kind=='law':
  panel(d,(110,470,860,260),T('ДО УБИЙСТВА','BEFORE THE KILLING'),T('Страх перед Макэлроем','Fear of McElroy'),GOLD)
  route(d,[(540,760),(540,900)],min(1,p*2),TEAL)
  panel(d,(110,950,860,290),T('ПОСЛЕ УБИЙСТВА','AFTER THE KILLING'),T('Никто не привлечён к ответственности','No one held accountable'),TEAL)
 elif kind in ['silent','question','ending']:
  pic=ImageOps.contain(load('town'),(1080,680));im.paste(pic,((1080-pic.width)//2,420));d=ImageDraw.Draw(im)
  txt(d,(540,1170),T('СТРАХ → МОЛЧАНИЕ','FEAR → SILENCE'),49,GOLD)
  if kind in ['question','ending']:txt(d,(540,1330),T('ГДЕ ГРАНИЦА СПРАВЕДЛИВОСТИ?','WHERE DOES JUSTICE END?'),42)
 return im
