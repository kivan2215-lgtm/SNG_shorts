"""Narration-led visual revision: action scenes and explanatory motion, no camera shake."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from functools import lru_cache
import math,json
from visuals import font,txt,base,photo,load,BG,INK,GOLD,TEAL,RED,MUTED,render as old_render
A=Path(__file__).parent/'assets'
def ease(p):return max(0,min(1,p))**2*(3-2*max(0,min(1,p)))
@lru_cache(12)
def action(sheet,i):
 im=Image.open(A/f'actions_{sheet}.png').convert('RGB');w,h=im.size
 if sheet=='c':box=(i*w//2+5,4,(i+1)*w//2-5,h-4)
 else:box=((i%2)*w//2+5,(i//2)*h//2+5,(i%2+1)*w//2-5,(i//2+1)*h//2-5)
 return im.crop(box)
def place(im,pic,box,cover=False):
 x,y,w,h=box
 pic=(ImageOps.fit if cover else ImageOps.contain)(pic,(w,h),Image.Resampling.LANCZOS)
 im.paste(pic,(int(x+(w-pic.width)/2),int(y+(h-pic.height)/2)))
def scene(sheet,i,title,detail=''):
 im=base(title);place(im,action(sheet,i),(0,335,1080,1110))
 if detail:
  d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1320,1080,1445),fill=(8,18,28,215));txt(d,(540,1380),detail,40,GOLD)
 return im
def badge(d,box,label,color=GOLD,n=36):
 x,y,w,h=box;d.rounded_rectangle((x,y,x+w,y+h),18,fill='#152938',outline=color,width=2);txt(d,(x+w/2,y+h/2),label,n,color,w=w-40)
def arrow(d,pts,p,color=GOLD,width=7):
 lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])];left=sum(lengths)*ease(p);end=pts[0];lastangle=0
 for a,b,l in zip(pts,pts[1:],lengths):
  if left<=0:break
  q=min(1,left/l);end=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);d.line((a,end),fill=color,width=width);left-=l;lastangle=math.atan2(b[1]-a[1],b[0]-a[0])
 if p>0:
  tip=end;back=(tip[0]-20*math.cos(lastangle),tip[1]-20*math.sin(lastangle));perp=(-10*math.sin(lastangle),10*math.cos(lastangle));d.polygon([tip,(back[0]+perp[0],back[1]+perp[1]),(back[0]-perp[0],back[1]-perp[1])],fill=color)
def man(d,x,y,s=1,c=TEAL):
 # Grounded figures with faces, sleeves, legs and shadows; decorative people not an exact witness count.
 d.ellipse((x-25*s,y+65*s,x+34*s,y+80*s),fill='#15222c')
 skin='#c7aa8d';d.ellipse((x-12*s,y-39*s,x+12*s,y-14*s),fill=skin);d.pieslice((x-13*s,y-43*s,x+13*s,y-18*s),180,360,fill='#554b40')
 d.polygon([(x-19*s,y-10*s),(x+17*s,y-10*s),(x+23*s,y+25*s),(x-23*s,y+25*s)],fill=c)
 d.line((x-13*s,y-4*s,x-28*s,y+31*s),fill=c,width=max(2,int(12*s)));d.line((x+14*s,y-4*s,x+29*s,y+28*s),fill=c,width=max(2,int(12*s)))
 for xx in [-11,11]:d.line((x+xx*s,y+23*s,x+xx*s,y+66*s),fill='#6d7b82',width=max(2,int(13*s)));d.ellipse((x+(xx-9)*s,y+61*s,x+(xx+12)*s,y+73*s),fill='#111b21')
def street(p,T,reveal=False):
 im=base(T('ЛЮДИ ВОКРУГ ПИКАПА','PEOPLE AROUND THE PICKUP'));d=ImageDraw.Draw(im)
 # Deliberately a relational illustration, no precise site geometry or firing positions.
 d.polygon([(40,630),(1050,560),(1050,1400),(40,1470)],fill='#4e626d');d.polygon([(40,630),(1050,560),(1050,650),(40,720)],fill='#b2aa96')
 for x in range(65,1080,95):d.line((x,640,x+35,696),fill='#817f76',width=2)
 d.polygon([(65,365),(1010,365),(1010,570),(65,640)],fill='#8b8775');d.polygon([(65,365),(990,315),(1030,365),(65,425)],fill='#5a5d56')
 for x in [130,405,680]:
  d.rectangle((x,440,x+170,570),fill='#344b58',outline='#b6b09c',width=4);d.line((x+85,440,x+85,570),fill='#abac9c',width=3)
 badge(d,(350,365,380,75),'D&G',GOLD,43)
 # Truck in three-quarter view, complete body, glass and wheels.
 dx=int(30*(1-ease(p*2))) if reveal else 0;x=220+dx;y=860
 d.ellipse((x+10,y+190,x+610,y+270),fill='#2f414c')
 for xx in [115,475]:d.ellipse((x+xx-46,y+155,x+xx+46,y+249),fill='#101b22');d.ellipse((x+xx-23,y+179,x+xx+23,y+225),fill='#9eaaab')
 d.polygon([(x,y+60),(x+520,y+25),(x+625,y+95),(x+625,y+190),(x+30,y+232),(x,y+185)],fill='#a35749',outline='#d99f83')
 d.polygon([(x+50,y+50),(x+90,y-105),(x+280,y-126),(x+360,y+23)],fill='#a95a49',outline='#dec4a1')
 d.polygon([(x+105,y-87),(x+250,y-100),(x+307,y+10),(x+80,y+30)],fill='#73919d',outline='#c7c9b6');d.line((x+205,y-96,x+219,y+17),fill='#bfbda5',width=5)
 d.polygon([(x+375,y+50),(x+500,y+40),(x+585,y+100),(x+410,y+115)],fill='#624841');d.line((x+37,y+168,x+606,y+123),fill='#e1cbb0',width=6)
 d.rectangle((x+10,y+93,x+32,y+132),fill='#e9dba8');d.line((x+39,y+71,x+39,y+179),fill='#b8c0b9',width=6)
 points=[(150,765),(300,710),(490,705),(685,700),(880,740),(955,900),(910,1090),(765,1245),(520,1290),(270,1305),(115,1150),(90,945)]
 cols=['#8eaeb1','#b4a082','#859eae','#9a9c81']
 for i,(px,py) in enumerate(points):
  off=int(16*(1-ease(min(1,p*2+i*.03)))) if reveal else 0;man(d,px,py+off,.83,cols[i%4])
 txt(d,(540,1370),T('ПИКАП • КЕН И ЕГО ЖЕНА','PICKUP • KEN AND HIS WIFE'),37,GOLD)
 if reveal:badge(d,(265,485,550,75),T('ОЧЕВИДЦЫ РЯДОМ','WITNESSES NEARBY'),TEAL,33)
 return im
@lru_cache(1)
def boundaries():return json.loads((A/'us-states.json').read_text())['features']
def polys(f):return f['geometry']['coordinates'] if f['geometry']['type']=='Polygon' else [p[0] for p in f['geometry']['coordinates']]
def map_scene(lang,p):
 T=lambda a,b:a if lang=='ru' else b
 im=base(T('СКИДМОР • МИССУРИ','SKIDMORE • MISSOURI'));d=ImageDraw.Draw(im)
 d.rounded_rectangle((60,380,1020,970),25,fill='#1c3444',outline='#4b6978',width=2)
 def xy(lon,lat):return (90+(lon+125)/59*900,880-(lat-24)/26*450)
 for f in boundaries():
  if f['properties']['name'] in ['Alaska','Hawaii','Puerto Rico']:continue
  for ring in polys(f):
   pts=[xy(lon,lat) for lon,lat,*_ in ring];d.polygon(pts,fill=GOLD if f['properties']['name']=='Missouri' else '#3e5b6a',outline='#8aa1a8')
 x,y=xy(-95.078,40.289);radius=15+int(12*(.5-.5*math.cos(p*math.pi*3)))
 d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=INK,width=3);d.ellipse((x-5,y-5,x+5,y+5),fill=INK)
 txt(d,(540,440),T('США • СЕВЕРО-ЗАПАД МИССУРИ','USA • NORTHWESTERN MISSOURI'),33,INK)
 arrow(d,[(x,y+20),(x,1010),(250,1010)],min(1,p*2),GOLD)
 badge(d,(80,1040,920,150),T('СКИДМОР — НЕБОЛЬШОЙ ГОРОД','SKIDMORE — A SMALL TOWN'),GOLD,42)
 txt(d,(540,1320),'1981',110,INK)
 return im

def render(lang,kind,p=1):
 T=lambda a,b:a if lang=='ru' else b
 if kind in ['opening','portrait','history','death','wife','later','fear']:return old_render(lang,kind,p)
 if kind in ['witnesses','surrounded']:return street(p,T,kind=='surrounded')
 if kind=='denial':return scene('c',0,T('ПОЧТИ ВСЕ: НЕ ВИДЕЛИ СТРЕЛЯВШЕГО','ALMOST ALL: DID NOT SEE THE SHOOTER'))
 if kind=='location':return map_scene(lang,p)
 if kind=='intimidation':return scene('b',0,T('ЗАПУГИВАЛ СВИДЕТЕЛЕЙ','HE INTIMIDATED WITNESSES'))
 if kind=='store':return scene('a',0,T('ОН ВЫСТРЕЛИЛ В ВЛАДЕЛЬЦА МАГАЗИНА','HE SHOT THE GROCERY STORE OWNER'))
 if kind=='survived':return scene('a',1,T('ВЛАДЕЛЕЦ МАГАЗИНА ВЫЖИЛ','THE GROCER SURVIVED'))
 if kind=='tavern':return scene('a',3,T('В БАР — СНОВА С ОРУЖИЕМ','BACK TO THE BAR WITH A GUN'))
 if kind=='meeting':return scene('b',1,T('ЖИТЕЛИ ОБСУЖДАЮТ ЗАЩИТУ','RESIDENTS DISCUSS THEIR SAFETY'),T('10 июля 1981','10 July 1981'))
 if kind=='move':return scene('b',2,T('ЛЮДИ ИДУТ К БАРУ','THE CROWD HEADS TO THE BAR'))
 if kind=='pickup':return scene('b',3,T('КЕН САДИТСЯ В ПИКАП','KEN GETS INTO HIS PICKUP'))
 if kind=='investigation':return scene('c',1,T('ДЕЛОМ ЗАНЯЛОСЬ ФБР','THE FBI INVESTIGATED'))
 if kind=='verdict':
  im=base(T('СУД ПРИЗНАЛ ЕГО ВИНОВНЫМ','THE JURY FOUND HIM GUILTY'));place(im,Image.open(A/'courtroom_v2.png').convert('RGB'),(0,335,1080,1110));d=ImageDraw.Draw(im,'RGBA')
  if p>.12:
   d.rectangle((0,1305,1080,1445),fill=(9,23,34,225));txt(d,(540,1370),T('ПРИГОВОР ЗА НАПАДЕНИЕ','CONVICTED OF ASSAULT'),43,GOLD)
  return im
 if kind=='bail':
  im=scene('a',2,T('ВЫШЕЛ ПОД ЗАЛОГ','RELEASED ON BOND'));d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1115,1080,1445),fill=(9,23,34,228))
  badge(d,(45,1140,430,115),T('ПРИГОВОР ЕСТЬ','CONVICTED'),GOLD,33);badge(d,(605,1140,430,115),T('НА СВОБОДЕ','RELEASED'),RED,33)
  arrow(d,[(490,1200),(590,1200)],min(1,p*2),GOLD)
  txt(d,(540,1345),T('ПОКА РАССМАТРИВАЕТСЯ АПЕЛЛЯЦИЯ','WHILE THE APPEAL WAS PENDING'),36,INK)
  return im
 if kind=='threats':
  im=base(T('СНОВА УГРОЖАЛ ВЛАДЕЛЬЦУ','HE THREATENED THE GROCER AGAIN'))
  place(im,action('a',3),(40,385,470,680));place(im,action('a',1),(570,385,470,680));d=ImageDraw.Draw(im)
  badge(d,(45,1080,465,85),T('МАКЭЛРОЙ В БАРЕ','McELROY AT THE BAR'),GOLD,30);badge(d,(570,1080,465,85),T('ВЛАДЕЛЕЦ МАГАЗИНА','THE GROCER'),TEAL,30)
  arrow(d,[(270,1190),(270,1285),(815,1285),(815,1190)],min(1,p*1.7),RED,8)
  txt(d,(540,1380),T('АДРЕСАТ НОВЫХ УГРОЗ','THE TARGET OF NEW THREATS'),35,RED)
  return im
 if kind=='arrival':
  im=base(T('МАКЭЛРОЙ И ЖЕНА — У БАРА','McELROY AND HIS WIFE AT THE BAR'));place(im,load('tavern'),(0,360,1080,650));d=ImageDraw.Draw(im)
  place(im,load('portrait'),(80,1070,260,250));place(im,load('trena'),(390,1070,260,250));d=ImageDraw.Draw(im)
  badge(d,(745,1085,260,205),'D&G',GOLD,60);arrow(d,[(670,1190),(725,1190)],min(1,p*2),GOLD)
  txt(d,(370,1380),T('КЕН И ТРЕНА','KEN AND TRENA'),38,INK,w=680)
  return im
 if kind=='accounts':
  im=base(T('ПОКАЗАНИЯ НЕ СОВПАЛИ','THE ACCOUNTS DID NOT MATCH'))
  place(im,load('trena'),(60,390,470,510));place(im,action('c',0),(560,390,460,510));d=ImageDraw.Draw(im)
  badge(d,(60,930,470,160),T('ЖЕНА УЗНАЛА\nСТРЕЛЯВШЕГО','WIFE RECOGNIZED\nA GUNMAN'),GOLD,34)
  badge(d,(560,930,460,160),T('ДРУГИЕ ГОВОРИЛИ:\nНЕ ВИДЕЛИ','OTHERS SAID:\nDID NOT SEE'),TEAL,34)
  arrow(d,[(295,1120),(295,1220),(540,1220)],min(1,p*2),GOLD)
  arrow(d,[(790,1120),(790,1220),(540,1220)],min(1,p*2),TEAL)
  if p>.28:badge(d,(140,1290,800,130),T('ПРОТИВОРЕЧИЕ НЕ РАЗРЕШЕНО','THE CONFLICT WAS NOT RESOLVED'),RED,36)
  return im
 if kind=='nocharges':
  im=base(T('ОБВИНЕНИЙ НЕ ПРЕДЪЯВИЛИ','NO CHARGES WERE FILED'));place(im,action('c',1),(0,350,1080,670));d=ImageDraw.Draw(im)
  for i,(a,b) in enumerate([(T('МЕСТНОЕ\nРАССЛЕДОВАНИЕ','LOCAL\nINVESTIGATION'),T('БЕЗ\nОБВИНЕНИЙ','NO\nCHARGES')),(T('ФЕДЕРАЛЬНОЕ\nРАССЛЕДОВАНИЕ','FEDERAL\nINVESTIGATION'),T('БЕЗ\nОБВИНЕНИЙ','NO\nCHARGES'))]):
   y=1060+i*170;badge(d,(55,y,620,140),a,TEAL,35)
   arrow(d,[(690,y+70),(745,y+70)],min(1,p*2),GOLD)
   if p>.15:badge(d,(760,y,265,140),b,GOLD,32)
  return im
 if kind=='law':
  im=base(T('ЗАКОН НЕ ЗАЩИТИЛ — И НЕ НАКАЗАЛ','THE LAW FAILED TO PROTECT OR PUNISH'))
  place(im,load('ken_full'),(40,390,470,570));place(im,load('scene'),(570,390,470,570));d=ImageDraw.Draw(im)
  badge(d,(45,990,465,200),T('ДО УБИЙСТВА\nСТРАХ ПЕРЕД КЕНОМ','BEFORE THE KILLING\nFEAR OF KEN'),GOLD,32)
  badge(d,(570,990,465,200),T('ПОСЛЕ УБИЙСТВА\nНЕТ ОБВИНЕНИЙ','AFTER THE KILLING\nNO CHARGES'),TEAL,32)
  arrow(d,[(300,1250),(300,1340),(780,1340),(780,1250)],min(1,p*1.7),RED,7)
  return im
 if kind in ['silent','question','ending']:
  title=T('ГОРОД ПРОДОЛЖИЛ МОЛЧАТЬ','THE TOWN KEPT ITS SILENCE') if kind=='silent' else T('ГДЕ ГРАНИЦА СПРАВЕДЛИВОСТИ?','WHERE DOES JUSTICE END?')
  im=base(title);place(im,load('town'),(0,350,1080,730));d=ImageDraw.Draw(im)
  if kind=='silent':badge(d,(80,1150,920,220),T('ДЕСЯТИЛЕТИЯ БЕЗ РАЗГАДКИ','DECADES WITHOUT AN ANSWER'),GOLD,45)
  else:
   left=T('СПРАВЕДЛИВОСТЬ?','JUSTICE?');right=T('ИЛИ УБИЙСТВО?','OR MURDER?')
   badge(d,(60,1150,465,220),left,GOLD if kind=='question' else MUTED,40)
   if kind=='ending':badge(d,(555,1150,465,220),right,TEAL,40)
  return im
 raise ValueError(kind)
