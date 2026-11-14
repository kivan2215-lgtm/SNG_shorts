"""Squalus: cohesive explanatory animation, with unaltered source archives.
All geometry is explanatory, not a recovered engineering drawing of the hull.
"""
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from pathlib import Path
from functools import lru_cache
import math,numpy as np
P=Path(__file__).parent;A=P/'assets';W,H=1080,1920
INK='#eeeae1';GOLD='#f4cb7f';BLUE='#5acadd';MUTE='#8daeb8';RED='#ed927d';GREEN='#a4e2bd'
@lru_cache(80)
def font(n,bold=True):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',int(n))
def text(d,xy,s,n=42,c=INK,anchor='mm',width=900):
 n=int(n)
 while max(font(n).getlength(z) for z in s.split('\n'))>width:n-=1
 d.multiline_text(xy,s,font=font(n),fill=c,anchor=anchor,align='center',spacing=14)
def lerp(a,b,p):return a+(b-a)*p
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def seg(p,a,b):return ease((p-a)/(b-a))
@lru_cache(5)
def backdrop(style='ocean'):
 y,x=np.mgrid[0:H,0:W];v=np.maximum(0,1-np.sqrt(((x-480)/1100)**2+((y-650)/1700)**2))
 colors=(np.array([3,12,21]),np.array([8,27,34])) if style=='ocean' else (np.array([9,14,20]),np.array([19,28,34]))
 a=colors[0]+v[:,:,None]*colors[1];im=Image.fromarray(a.astype('uint8'));d=ImageDraw.Draw(im)
 rng=np.random.default_rng(32)
 for k in range(170):
  px=int(rng.integers(0,W));py=int(rng.integers(300,1800));d.ellipse((px,py,px+1,py+1),fill='#31505a')
 return im

def title(im,head,sub=None):
 d=ImageDraw.Draw(im);d.line((80,166,143,166),fill=GOLD,width=4)
 text(d,(80,206),head,47,INK,anchor='la',width=890)
 if sub:text(d,(80,274),sub,29,MUTE,anchor='la',width=890)
 return d
@lru_cache(16)
def photo(name):
 files=list(A.glob(name+'.*'));return Image.open(next(f for f in files if f.suffix in ['.jpg','.png'])).convert('RGB')
def fit(im,pic,box):
 x,y,w,h=box;pic=ImageOps.contain(pic,(w,h),Image.Resampling.LANCZOS);im.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
def linearrow(d,pts,p=1,col=GOLD,th=5):
 lens=[math.dist(a,b) for a,b in zip(pts,pts[1:])];remain=sum(lens)*max(0,min(1,p));end=pts[0];angle=0
 for a,b,l in zip(pts,pts[1:],lens):
  if remain<=0:break
  q=min(1,remain/l);end=(lerp(a[0],b[0],q),lerp(a[1],b[1],q));d.line([a,end],fill=col,width=th);angle=math.atan2(b[1]-a[1],b[0]-a[0]);remain-=l
 if p>0:
  b=(end[0]-18*math.cos(angle),end[1]-18*math.sin(angle));d.polygon([end,(b[0]-9*math.sin(angle),b[1]+9*math.cos(angle)),(b[0]+9*math.sin(angle),b[1]-9*math.cos(angle))],fill=col)
def bolt(d,x,y,r=4):d.ellipse((x-r,y-r,x+r,y+r),fill='#b1b9b7',outline='#26383d',width=1)
def person(d,x,y,size=1,col='#d6d1bf',pose='stand'):
 # Coherent neutral human silhouette, not evidence of exact positions/headcount.
 s=size
 def pt(a,b):return x+a*s,y+b*s
 d.ellipse((*pt(-8,-59),*pt(8,-43)),fill=col)
 d.polygon([pt(-11,-40),pt(10,-40),pt(15,-14),pt(7,-8),pt(5,13),pt(-2,13),pt(-3,-8),pt(-9,13),pt(-16,13),pt(-12,-12)],fill=col)
 d.line([pt(-10,-36),pt(-19,-17),pt(-23,-11)],fill=col,width=max(2,int(6*s)))
 d.line([pt(10,-36),pt(20,-21),pt(22,-7)],fill=col,width=max(2,int(6*s)))

def sub(d,x,y,w,cut=False,water=0,door=1):
 h=w*.22;left=x;right=x+w;top=y;bot=y+h
 # Outer casing and pressure hull.
 d.rounded_rectangle((x,y,x+w,y+h),radius=h/2,fill='#253d49',outline='#91a3a4',width=3)
 for i in range(3,int(h)-2):
  yy=y+i;c=int(32+50*math.sin(math.pi*i/h));inset=h/2-math.sqrt(max(0,(h/2-3)**2-(i-h/2)**2))
  d.line((x+inset,yy,x+w-inset,yy),fill=(c,c+17,c+23),width=1)
 for frac in [.17,.29,.42,.55,.68,.80]:
  xx=x+w*frac;d.line((xx,y+5,xx,y+h-4),fill='#60747a',width=1)
 for frac in [.14,.2,.26,.32,.38,.65,.71,.77,.83]:
  xx=x+w*frac;d.line((xx,y,xx,y-22),fill='#8da7a9',width=2)
 d.line((x+w*.14,y-22,x+w*.83,y-22),fill='#8da7a9',width=2)
 for frac in [.65,.68,.71,.74,.77,.8,.83]:
  xx=x+w*frac;d.ellipse((xx,y+18,xx+6,y+24),fill='#15282e')
 d.line((x+w*.12,top+8,x+w*.88,top+8),fill='#aab8b5',width=3)
 d.rounded_rectangle((x+w*.43,y-h*.45,x+w*.57,y+8),radius=11,fill='#48626a',outline='#8eaaa9',width=2)
 d.ellipse((x+w*.47,y-h*.28,x+w*.50,y-h*.12),outline='#a9bfbd',width=2)
 d.line((x+w*.34,y-25,x+w*.34,y-45),fill='#9daba7',width=5)
 d.line((x+w*.30,y-44,x+w*.39,y-44),fill='#aab8b1',width=7)
 for frac in [.47,.52]:d.line((x+w*frac,y-h*.45,x+w*frac,y-h*.85),fill='#91a3a4',width=4)
 d.line((right-30,y+h/2,right+15,y+h/2),fill='#70898c',width=7)
 d.ellipse((right+8,y+h*.24,right+22,y+h*.78),outline='#a29b7c',width=4)
 hx=x+w*.27;d.rounded_rectangle((hx-24,y-20,hx+24,y+8),6,fill='#667f82',outline=GOLD,width=2)
 if cut:
  ix=x+w*.13;iy=y+h*.19;iw=w*.73;ih=h*.62
  d.rounded_rectangle((ix,iy,ix+iw,iy+ih),12,fill='#13262c',outline='#a8b3ae',width=3)
  # Foreground floor, pipes and distinct rooms; bow at left.
  for yy in [iy+12,iy+ih-14]:d.line((ix+8,yy,ix+iw-8,yy),fill='#546669',width=4)
  for frac in [.20,.4,.60,.8]:
   xx=ix+iw*frac;d.line((xx,iy,xx,iy+ih),fill='#617779',width=3)
  for j in range(3):
   xx=ix+iw*.54+j*iw*.13;d.rounded_rectangle((xx,iy+20,xx+iw*.095,iy+ih-23),5,fill='#405258',outline='#6e8183',width=2)
   for k in range(4):d.line((xx+4,iy+30+k*12,xx+iw*.095-4,iy+30+k*12),fill='#82908f',width=2)
  if water:
   bx=ix+iw*.45;by=min(iy+ih-3,iy+ih*(1-water));d.rectangle((bx,by,ix+iw-2,iy+ih-3),fill='#226878')
   for xx in range(int(bx),int(ix+iw),20):d.arc((xx,by-4,xx+20,by+5),0,180,fill='#7bc1c9',width=2)
  xx=ix+iw*.45;d.rectangle((xx-5,iy,xx+7,iy+ih*door),fill=GOLD)
  for j in range(4):person(d,ix+25+j*iw*.095,iy+ih-14,size=ih/115,col='#d4bc85')
 return hx,y

def ocean_depth(d,lang,amount=1):
 T=lambda a,b:a if lang=='ru' else b
 d.line((70,400,1010,400),fill='#7baab7',width=3)
 text(d,(750,355),T('ПОВЕРХНОСТЬ','SURFACE'),27,MUTE,anchor='la',width=280)
 for y,m in [(420,0),(660,20),(900,40),(1140,60),(1308,74)]:
  d.line((913,y,936,y),fill=MUTE,width=2)
  text(d,(950,y),str(m if lang=='ru' else round(m*243/74)),25,MUTE,anchor='lm',width=100)
 d.line((923,420,923,1308),fill='#42616e',width=2)
 d.line((880,420,880,420+888*amount),fill=GOLD,width=4)
 text(d,(730,550),T('74 м','243 ft'),78,GOLD,width=300)
 # Sea floor, not oscillating camera.
 d.polygon([(0,1380),(100,1355),(260,1370),(420,1346),(600,1375),(800,1353),(1080,1385),(1080,1750),(0,1750)],fill='#13272d')
 for x in range(30,1080,46):d.line((x,1405+(x%38),x+27,1410+(x%38)),fill='#2c4348',width=2)

def bell(d,cx,top,s=1,water=1,hatch=0,passenger=0,seal=False):
 # Pear-shaped upper chamber + lower mating skirt. Coordinates local to this drawing.
 def pt(x,y):return cx+x*s,top+y*s
 def box(x1,y1,x2,y2):return (*pt(x1,y1),*pt(x2,y2))
 poly=[pt(-155,510)]+[pt(155*math.cos(a),185+185*math.sin(a)) for a in np.linspace(math.pi,2*math.pi,65)]+[pt(155,510),pt(122,575),pt(-122,575)]
 d.polygon(poly,fill='#778c8c')
 # Curved top and bevelled steel side shell, with structural highlights.
 for yy in range(0,575,2):
  if yy<185:half=155*math.sqrt(max(0,1-((185-yy)/185)**2))
  elif yy<510:half=155
  else:half=155-(yy-510)*33/65
  c=int(64+55*(1-yy/575));d.line([pt(-half,yy),pt(half,yy)],fill=(c,c+17,c+17),width=max(2,int(2*s)))
 d.line(poly+[poly[0]],fill='#bed0c8',width=max(2,int(4*s)))
 inside=[pt(-133,490)]+[pt(133*math.cos(a),190+166*math.sin(a)) for a in np.linspace(math.pi,2*math.pi,65)]+[pt(133,490),pt(105,553),pt(-105,553)]
 d.polygon(inside,fill='#172d35')
 # A broad steel rim communicates shell thickness, with a lit interior.
 for yy in range(155,290,2):
  c=int(28+12*math.sin((yy-155)/135*math.pi));d.line([pt(-120,yy),pt(120,yy)],fill=(c,c+20,c+21),width=max(2,int(2*s)))
 d.line([pt(-127,185),pt(-127,280)],fill='#788e88',width=max(2,int(4*s)))
 d.line([pt(126,185),pt(126,280)],fill='#5a746f',width=max(2,int(4*s)))
 d.rectangle(box(-25,53,30,65),fill='#f4ddb0')
 for yy in [153,172]:d.line([pt(-115,yy),pt(-50,yy)],fill='#91a29a',width=max(2,int(3*s)))
 # Side wall strip + rivets create readable steel thickness.
 for yy in range(190,490,45):
  for xx in [-145,145]:bolt(d,*pt(xx,yy),max(2,int(3*s)))
 # air hose enters upper chamber and bends down the wall
 d.line([pt(65,-150),pt(65,-36),pt(105,30),pt(115,200)],fill='#bda375',width=max(2,int(7*s)))
 d.line([pt(-30,-180),pt(-30,-20),pt(0,-10)],fill='#92b3bd',width=max(2,int(4*s)))
 d.ellipse(box(-15,-24,15,4),outline=INK,width=max(2,int(4*s)))
 # Interior seats, gauge and operator, communications and ladder.
 d.rounded_rectangle(box(-124,246,-43,268),radius=4,fill='#8f7a56')
 d.ellipse(box(66,85,104,123),fill='#dad9cb',outline='#7a8d91',width=2)
 d.line([pt(85,104),pt(94,96)],fill='#293d42',width=2)
 d.ellipse(box(60,145,109,194),outline='#aaa480',width=max(2,int(3*s)))
 d.line([pt(85,145),pt(85,194)],fill='#aaa480',width=max(2,int(2*s)))
 d.line([pt(60,170),pt(109,170)],fill='#aaa480',width=max(2,int(2*s)))
 d.line([pt(-105,53),pt(-105,227)],fill='#c3c8b9',width=max(2,int(3*s)))
 person(d,*pt(-60,282),size=s*.85,col='#c5bea4')
 # Main floor seals upper compartment during descent.
 d.rectangle(box(-133,300,133,315),fill='#7d9290')
 for xx in [-42,42]:d.line([pt(xx,324),pt(xx,546)],fill='#8faaa8',width=max(2,int(3*s)))
 for yy in range(335,540,26):d.line([pt(-42,yy),pt(42,yy)],fill='#93a6a0',width=max(2,int(3*s)))
 # lower wet chamber before dewatering
 if water>0:
  d.rectangle(box(-125,lerp(550,320,water),125,550),fill='#23778b')
  for yy in range(int(lerp(550,320,water))+10,548,25):d.line([pt(-120,yy),pt(120,yy)],fill='#338b9b',width=1)
 # central hatch cover pivots away in the explanatory section
 angle=ease(hatch)*1.4
 d.line([pt(-45,302),pt(-45+90*math.cos(angle),302-90*math.sin(angle))],fill=GOLD,width=max(3,int(9*s)))
 d.rectangle(box(-132,554,132,575),fill='#182322',outline=GREEN if seal else '#94a49c',width=max(2,int(4*s)))
 if passenger>0:
  person(d,*pt(20,lerp(650,255,ease(passenger))),size=s*.88,col=GOLD)

def close_chamber(lang,mode,p):
 T=lambda a,b:a if lang=='ru' else b;im=backdrop().copy();d=ImageDraw.Draw(im)
 heads={'dock':T('СОВМЕСТИТЬ С ЛЮКОМ','ALIGN WITH THE HATCH'),'seal':T('МОРЕ ОСТАЁТСЯ СНАРУЖИ','KEEP THE SEA OUT'),'drain':T('СНАЧАЛА — УБРАТЬ ВОДУ','FIRST, REMOVE THE WATER'),'dry':T('ПОЯВИЛСЯ СУХОЙ ПРОХОД','A DRY PASSAGE'),'open':T('ТЕПЕРЬ МОЖНО ОТКРЫТЬ','NOW THE HATCHES CAN OPEN'),'transfer':T('ИЗ ЛОДКИ — В КАМЕРУ','FROM SUB TO CHAMBER'),'question':T('КАК ОТКРЫТЬ ЛЮК?','HOW CAN THE HATCH OPEN?'),'cable':T('ТРОС ВЕДЁТ К ЛЮКУ','THE CABLE GUIDES THE WAY')}
 title(im,heads[mode],T('МЕХАНИЗМ СПАСЕНИЯ','HOW THE RESCUE WORKED'))
 # hull section large at lower screen
 for yy in range(1250,1440):
  q=(yy-1250)/190;c=int(40+25*math.sin(q*math.pi));d.line((0,yy,1080,yy),fill=(c,c+18,c+21))
 d.line((0,1250,1080,1250),fill='#92a7a6',width=5)
 d.rectangle((380,1210,700,1260),fill='#698483',outline='#bdd0c3',width=3)
 d.rectangle((435,1225,645,1440),fill='#1b323a')
 for xx in range(25,1080,46):bolt(d,xx,1273,5)
 d.line((475,1260,475,1430),fill='#a3b8af',width=5);d.line((605,1260,605,1430),fill='#a3b8af',width=5)
 for yy in range(1280,1420,34):d.line((475,yy,605,yy),fill='#9cb7ad',width=4)
 if mode=='question':
  d.line((436,1218,644,1218),fill=GOLD,width=12)
  for x in [430,540,650]:linearrow(d,[(x,650),(x,1140)],seg(p,.1,.65),BLUE,6)
  text(d,(540,535),T('СНАРУЖИ — ВОДА','WATER OUTSIDE'),38,BLUE)
  text(d,(540,1360),T('ВНУТРИ — ЛЮДИ','PEOPLE INSIDE'),37,GOLD)
  return im
 if mode=='cable':
  d.line((540,400,540,1210),fill=GOLD,width=6)
  d.arc((514,1178,566,1230),0,325,fill=GOLD,width=6)
  # Working diver visibly attaches cable, with hose continuing upward.
  dx=lerp(760,630,ease(p));dy=1010
  d.line([(780,360),(810,650),(dx+20,dy-55)],fill='#b59b65',width=6)
  d.ellipse((dx-27,dy-105,dx+27,dy-48),fill='#b4965c',outline=GOLD,width=4)
  d.ellipse((dx-13,dy-92,dx+13,dy-68),fill='#192d34',outline='#dac382',width=3)
  d.rounded_rectangle((dx-27,dy-45,dx+27,dy+55),15,fill='#9d977a',outline='#c5bd94',width=2)
  d.line([(dx-19,dy+45),(dx-31,dy+125),(dx-65,dy+133)],fill='#9d977a',width=22)
  d.line([(dx+16,dy+45),(dx+43,dy+113),(dx+83,dy+119)],fill='#9d977a',width=22)
  d.line([(dx-19,dy-30),(dx-50,dy+45),(545,1210)],fill='#aea489',width=16)
  text(d,(290,680),T('ТРОС','GUIDE CABLE'),34,GOLD,width=350);d.line((400,700,535,735),fill=GOLD,width=3)
  text(d,(760,1350),T('ЛЮК','HATCH'),33,INK,width=180)
  return im
 dock=seg(p,0,.7) if mode=='dock' else 1
 by=lerp(260,376,dock);scale=1.45;bottom=by+575*scale
 water=1 if mode in ('dock','seal') else (1-seg(p,.10,.8) if mode=='drain' else 0)
 hatch=seg(p,.08,.75) if mode=='open' else (1 if mode=='transfer' else 0)
 # fixed guiding line ahead of chamber arrival
 d.line((540,400,540,1210),fill='#d9bc79',width=3)
 bell(d,540,by,scale,water,hatch,seg(p,.05,.9) if mode=='transfer' else 0,mode!='dock' or p>.75)
 if mode in ('seal','drain','dry','open','transfer'):
  d.ellipse((375,1195,705,1230),outline=GREEN,width=6)
 if mode=='seal':
  text(d,(170,1060),T('РЕЗИНОВОЕ\nКОЛЬЦО','RUBBER\nSEAL'),27,GREEN,width=245);linearrow(d,[(235,1120),(400,1210)],seg(p,.2,.7),GREEN)
  for x,xx in [(150,360),(930,720)]:linearrow(d,[(x,850),(xx,850)],seg(p,.1,.6),BLUE)
 if mode=='drain':
  text(d,(845,1040),T('ВОДА','WATER'),32,BLUE,width=200)
  linearrow(d,[(690,1080),(825,1080),(825,1210)],seg(p,.2,.8),BLUE)
 if mode in ('dry','open','transfer'):
  text(d,(170,1030),T('СУХОЙ\nПРОХОД','DRY\nPASSAGE'),29,GREEN,width=245)
  d.line((230,1100,430,1110),fill=GREEN,width=3)
 # submarine hatch opens only after dewatering; upper and lower covers shown separately
 ang=ease(hatch)*1.3;d.line((435,1220,435+210*math.cos(ang),1220+130*math.sin(ang)),fill=GOLD,width=10)
 if mode=='transfer':linearrow(d,[(840,1390),(840,940)],seg(p,.15,.8),GREEN)
 im.paste(backdrop().crop((0,0,1080,335)),(0,0))
 title(im,heads[mode],T('МЕХАНИЗМ СПАСЕНИЯ','HOW THE RESCUE WORKED'))
 return im

def render(lang,k,p=0):
 T=lambda a,b:a if lang=='ru' else b
 if k=='hero':
  im=backdrop().copy();fit(im,photo('seabed'),(0,90,1080,1680));d=ImageDraw.Draw(im)
  text(d,(540,240),T('ПОДЛОДКА НА ДНЕ.','A SUBMARINE ON THE SEABED.'),55,INK)
  text(d,(540,330),T('ВНУТРИ — ЖИВЫЕ.','PEOPLE STILL ALIVE INSIDE.'),48,GOLD)
  return im
 if k in ['question','cable','dock','seal','drain','dry','open','transfer']:return close_chamber(lang,k,p)
 if k=='construction':
  im=backdrop('archive').copy();title(im,T('23 МАЯ 1939','23 MAY 1939'),T('АТЛАНТИКА • У БЕРЕГОВ США','ATLANTIC • OFF THE U.S. COAST'))
  fit(im,photo('construction'),(0,355,1080,1090));d=ImageDraw.Draw(im)
  text(d,(540,1378),T('«СКВОЛУС» • СТРОИТЕЛЬСТВО, 1938','SQUALUS • UNDER CONSTRUCTION, 1938'),27,GOLD,width=950)
  return im
 if k in ['loss','sealed']:
  im=backdrop().copy();d=ImageDraw.Draw(im)
  title(im,T('26 ЧЕЛОВЕК ПОГИБЛИ','26 PEOPLE LOST THEIR LIVES') if k=='loss' else T('ПЕРЕБОРКА ОСТАНОВИЛА ВОДУ','A BULKHEAD HELD BACK THE WATER'),T('НОС СЛЕВА • КОРМА СПРАВА','BOW LEFT • STERN RIGHT'))
  if k=='loss':
   sub(d,70,820,910,cut=True,water=1)
   text(d,(760,600),'26',130,RED,width=350)
   linearrow(d,[(760,690),(760,840)],seg(p,.1,.7),RED,5)
   text(d,(740,1180),T('ЗАТОПЛЕНО','FLOODED'),39,BLUE,width=450)
   text(d,(300,1180),T('СУХИЕ ОТСЕКИ','DRY SECTION'),35,GOLD,width=450)
  else:
   # A magnified explanatory section, with lamps, pipes, a wheel and an actual doorway.
   d.rounded_rectangle((80,465,1000,1320),radius=70,fill='#233c44',outline='#809c9d',width=5)
   for yy in [510,540,1220]:d.line((115,yy,965,yy),fill='#7f9997',width=7)
   d.rectangle((555,570,975,1260),fill='#25677d')
   for yy in range(610,1230,49):d.line((575,yy,960,yy),fill='#317b8c',width=2)
   for xx in [160,310,460,760,880]:d.line((xx,475,xx,1310),fill='#526a6c',width=3)
   for xx in [230,400]:
    d.rounded_rectangle((xx-35,560,xx+35,580),5,fill=GOLD)
   person(d,210,1130,2.3,col='#d4c4a0');person(d,365,1130,2.3,col='#b9b49a')
   d.rectangle((520,500,555,1290),fill='#879b94',outline='#cad4c8',width=3)
   # Watertight door closes the passage; the solid barrier stops incoming water.
   d.rounded_rectangle((475,740,587,1120),50,fill='#78918c',outline=GOLD,width=5)
   d.ellipse((485,865,575,955),outline=GOLD,width=6)
   ang=ease(p)*math.pi
   for a in [ang,ang+math.pi/2]:
    d.line((530+43*math.cos(a),910+43*math.sin(a),530-43*math.cos(a),910-43*math.sin(a)),fill=GOLD,width=5)
   linearrow(d,[(900,1000),(620,1000)],seg(p,.1,.6),BLUE,7)
   text(d,(320,1370),T('ЛЮДИ','PEOPLE'),36,GOLD,width=330)
   text(d,(790,1370),T('ВОДА','WATER'),36,BLUE,width=330)
  return im
 if k in ['dive','valve','flood','loss','sealed']:
  im=backdrop().copy();d=ImageDraw.Draw(im)
  titles={'dive':T('ИСПЫТАТЕЛЬНОЕ ПОГРУЖЕНИЕ','A TEST DIVE'),'valve':T('КЛАПАН НЕ ЗАКРЫЛСЯ','THE VALVE DID NOT CLOSE'),'flood':T('ВОДА УХОДИТ В КОРМУ','WATER FLOODS THE AFT SECTION'),'loss':T('ЗАТОПЛЕННЫЕ ОТСЕКИ','THE FLOODED COMPARTMENTS'),'sealed':T('ПУТЬ ВОДЕ ПЕРЕКРЫЛИ','THEY SEALED OFF THE WATER')}
  title(im,titles[k],T('НОС СЛЕВА • КОРМА СПРАВА','BOW LEFT • STERN RIGHT'))
  water=seg(p,.05,.9) if k=='flood' else (1 if k in ('loss','sealed') else 0)
  yy=lerp(820,1120,ease(p)) if k=='dive' else 1120
  sub(d,70,yy,910,cut=k!='dive',water=water)
  if k=='dive':
   d.line((50,540,1020,540),fill='#7babb6',width=3)
   linearrow(d,[(700,660),(700,950)],seg(p,.2,.8),BLUE)
   text(d,(330,620),T('ПОГРУЖЕНИЕ','DIVING'),35,BLUE)
  else:
   # large mechanical detail, linked to intake location
   d.line((570,1040,650,920),fill='#526e76',width=3)
   d.line((650,920,650,830),fill='#526e76',width=3)
   d.rounded_rectangle((200,430,880,875),radius=25,fill='#142b36',outline='#4b6e79',width=3)
   text(d,(540,475),T('ВОЗДУХОЗАБОРНИК','AIR INTAKE'),34,MUTE)
   # pipe and valve, visible opening
   d.line([(400,535),(400,700),(700,700),(700,825)],fill='#809795',width=100)
   d.line([(400,535),(400,700),(700,700),(700,825)],fill='#1c4656',width=72)
   d.line((370,610,440,570),fill=GOLD,width=13)
   for yy2 in [550,650]:linearrow(d,[(400,yy2),(400,yy2+36)],1,BLUE,5)
   linearrow(d,[(450,700),(670,700),(700,815)],ease(p) if k=='valve' else 1,BLUE,6)
   if k=='valve':text(d,(720,570),T('ОТКРЫТ','OPEN'),39,GOLD,width=250)
   elif k=='loss':text(d,(540,960),T('26 ПОГИБШИХ','26 LIVES LOST'),58,RED)
   elif k=='sealed':
    text(d,(320,960),T('СУХИЕ ОТСЕКИ','DRY COMPARTMENTS'),33,GOLD,width=450)
    linearrow(d,[(400,1000),(490,1165)],seg(p,.1,.6),GOLD)
   else:text(d,(540,960),T('ВОДА ЗАПОЛНЯЕТ КОРМУ','WATER FILLS THE AFT SECTION'),36,BLUE)
  return im
 if k=='trapped':
  im=backdrop().copy();fit(im,photo('inside'),(0,150,1080,1500));d=ImageDraw.Draw(im)
  text(d,(540,225),T('33 ЧЕЛОВЕКА В ЛОВУШКЕ','33 PEOPLE TRAPPED'),48,GOLD)
  return im
 if k in ['trapped','depth','lower','rise','trips','saved']:
  im=backdrop().copy();d=ImageDraw.Draw(im)
  heads={'trapped':T('33 ЧЕЛОВЕКА В ЛОВУШКЕ','33 PEOPLE TRAPPED'),'depth':T('ДО ПОВЕРХНОСТИ — 74 МЕТРА','243 FEET BELOW THE SURFACE'),'lower':T('КАМЕРА ИДЁТ К ЛОДКЕ','THE CHAMBER DESCENDS'),'rise':T('ПОДЪЁМ К ПОВЕРХНОСТИ','BACK TOWARD THE SURFACE'),'trips':T('ЧЕТЫРЕ РЕЙСА','FOUR RESCUE TRIPS'),'saved':T('33 ИЗ 33 СПАСЕНЫ','ALL 33 RESCUED')}
  title(im,heads[k]);ocean_depth(d,lang,seg(p,.05,.75) if k=='depth' else 1)
  sub(d,80,1235,735,cut=k=='trapped',water=1 if k=='trapped' else 0)
  if k in ('lower','rise','trips','saved'):
   # rescue vessel located over bow hatch; line connects to the same point
   d.polygon([(160,364),(550,364),(510,419),(210,419)],fill='#798f91',outline=INK)
   d.rectangle((280,310,420,364),fill='#9cabaa');d.rectangle((330,270,355,312),fill='#788c8d')
   d.line((280,310,280,265),fill='#b1bcb9',width=4)
   cx=278
   if k=='lower':by=lerp(480,1055,ease(p))
   elif k=='rise':by=lerp(1055,470,ease(p))
   elif k=='trips':by=470
   else:by=470
   d.line((cx,418,cx,by),fill=GOLD,width=3)
   bell(d,cx,by,.27,water=1)
   if k=='lower':linearrow(d,[(410,650),(410,1110)],seg(p,.1,.8),GOLD,5)
   elif k=='rise':linearrow(d,[(430,1100),(430,660)],seg(p,.1,.8),GREEN,5)
   elif k=='trips':
    for i in range(4):
     active=p>i/4;yy=720+i*110;d.ellipse((590,yy-26,642,yy+26),fill=GOLD if active else '#284b59')
     text(d,(616,yy),str(i+1),27,'#10202b' if active else MUTE,width=50)
     text(d,(745,yy),T('РЕЙС','TRIP'),28,INK if active else MUTE,width=190)
   else:
    text(d,(530,820),'33',180,GREEN,width=500);text(d,(530,980),T('ВЕРНУЛИСЬ ЖИВЫМИ','BROUGHT UP ALIVE'),38,INK)
  elif k=='trapped':
   text(d,(330,830),'33',170,GOLD,width=500)
   text(d,(330,970),T('ЖДУТ ПОМОЩИ','WAITING FOR HELP'),32,INK,width=470)
  return im
 if k in ['ships','divers','bell_archive','honors']:
  im=backdrop('archive').copy()
  heads={'ships':T('СПАСАТЕЛИ НАД ЛОДКОЙ','RESCUERS ABOVE THE WRECK'),'divers':T('РАБОТА НАЧИНАЕТСЯ С ВОДОЛАЗА','IT STARTS WITH A DIVER'),'bell_archive':T('КАМЕРА МАККЭННА','THE McCANN RESCUE CHAMBER'),'honors':T('ЛЮДИ, КОТОРЫЕ СПАСАЛИ','THE MEN BEHIND THE RESCUE')}
  subs={'ships':T('24 МАЯ 1939 • СПАСАТЕЛЬНАЯ ОПЕРАЦИЯ','24 MAY 1939 • RESCUE OPERATION'),'divers':T('ПОДГОТОВКА ВОДОЛАЗОВ • 1939','DIVERS PREPARING • 1939'),'bell_archive':T('ПОДЛИННЫЙ ЧЕРТЁЖ ВМС США','ORIGINAL U.S. NAVY CUTAWAY'),'honors':T('НАГРАЖДЕНИЕ • 19 ЯНВАРЯ 1940','MEDAL CEREMONY • 19 JANUARY 1940')}
  title(im,heads[k],subs[k]);name={'ships':'rescue_ships','divers':'divers','bell_archive':'bell_drawing','honors':'honors'}[k]
  fit(im,photo(name),(0,360,1080,1030));d=ImageDraw.Draw(im)
  if k=='ships':
   text(d,(300,1285),'WANDANK',29,MUTE,width=350);text(d,(790,1285),'FALCON',29,GOLD,width=350)
   d.line((300,1170,300,1230),fill=MUTE,width=2);d.line((790,1170,790,1230),fill=GOLD,width=2)
  if k=='bell_archive':
   text(d,(540,1410),T('ДВА ОТСЕКА • ГЕРМЕТИЧНОЕ СОЕДИНЕНИЕ','TWO COMPARTMENTS • A SEALED CONNECTION'),29,GOLD,width=980)
  if k=='honors':text(d,(540,1360),T('ЗА СПАСЕНИЕ И ПОДЪЁМ ПОДЛОДКИ','FOR THE RESCUE AND SALVAGE'),32,GOLD)
  return im
 if k=='final':
  im=backdrop().copy();d=ImageDraw.Draw(im)
  title(im,T('ВЫХОД ДОСТАВИЛИ НА ДНО','THEY BROUGHT THE WAY OUT DOWN'))
  # A clear final visual answer: closed submarine connected to chamber, ship above.
  d.line((80,440,1000,440),fill='#91c0c9',width=4)
  d.polygon([(280,398),(750,398),(690,445),(325,445)],fill='#728e99')
  d.rectangle((440,325,600,398),fill='#98a7a3')
  sub(d,90,1235,850,cut=False)
  d.line((320,440,320,630),fill=GOLD,width=4)
  bell(d,320,630,.65,water=1)
  linearrow(d,[(690,1250),(690,640)],seg(p,0,.7),GREEN,7)
  text(d,(720,920),'33',95,GREEN,width=280)
  text(d,(700,1030),T('ЖИВЫХ','ALIVE'),33,INK,width=300)
  return im
 raise ValueError(k)
