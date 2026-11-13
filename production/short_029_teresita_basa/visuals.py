from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from functools import lru_cache
import json,math
A=Path(__file__).parent/'assets';BG='#101d29';INK='#f5f1e8';GOLD='#e8bb6a';TEAL='#80c5bf';MUTE='#a7b4b9';RED='#cf8576'
@lru_cache(60)
def font(n,bold=True):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
def txt(d,xy,s,n=44,color=INK,w=930):
 while max(font(n).getlength(z) for z in s.split('\n'))>w:n-=1
 d.multiline_text(xy,s,font=font(n),fill=color,anchor='mm',align='center',spacing=14)
def base(title):
 im=Image.new('RGB',(1080,1920),BG);d=ImageDraw.Draw(im)
 for y in range(1920):
  q=max(0,1-abs(y-820)/1100);d.line((0,y,1080,y),fill=(int(13+6*q),int(24+11*q),int(35+13*q)))
 d.line((70,135,190,135),fill=GOLD,width=5);txt(d,(540,245),title,52)
 d.line((75,1740,1005,1740),fill='#334e5d',width=2)
 return im
def place(im,pic,box,cover=False):
 x,y,w,h=box;pic=(ImageOps.fit if cover else ImageOps.contain)(pic,(w,h),Image.Resampling.LANCZOS);im.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
@lru_cache(50)
def gen(sheet,i):
 im=Image.open(A/f'scenes_{sheet}.png').convert('RGB');w,h=im.size;col=i%2;row=i//2;return im.crop((col*w//2+5,row*h//2+5,(col+1)*w//2-5,(row+1)*h//2-5))
@lru_cache(10)
def archive(kind):
 im=Image.open(A/'people.jpg').convert('RGB');w,h=im.size
 if kind=='teresita':return im.crop((0,0,int(w*.595),h))
 if kind=='allan':return im.crop((int(w*.595),0,w,h))
 if kind=='news':
  im=Image.open(A/'dna.jpg').convert('RGB');return im.crop((0,0,int(im.width*.49),im.height))
 return im
def shot(sheet,i,title,sub=''):
 im=base(title);place(im,gen(sheet,i),(0,335,1080,1120))
 if sub:
  d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1315,1080,1455),fill=(7,18,28,215));txt(d,(540,1380),sub,39,GOLD)
 return im
def face(kind,title,sub=''):
 im=base(title);place(im,archive(kind),(0,345,1080,1100));d=ImageDraw.Draw(im)
 if sub:txt(d,(540,1380),sub,37,GOLD)
 return im
def badge(d,b,text,col=GOLD,n=36):
 x,y,w,h=b;d.rounded_rectangle((x,y,x+w,y+h),18,fill='#1c3443',outline=col,width=3);txt(d,(x+w/2,y+h/2),text,n,col,w=w-40)
def arrow(d,pts,p,col=GOLD):
 p=max(0,min(1,p));ls=[math.dist(a,b) for a,b in zip(pts,pts[1:])];left=p*sum(ls);end=pts[0];ang=0
 for a,b,l in zip(pts,pts[1:],ls):
  if left<=0:break
  q=min(1,left/l);end=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);d.line((a,end),fill=col,width=7);left-=l;ang=math.atan2(b[1]-a[1],b[0]-a[0])
 if p>0:
  v=(end[0]-21*math.cos(ang),end[1]-21*math.sin(ang));n=(-10*math.sin(ang),10*math.cos(ang));d.polygon([end,(v[0]+n[0],v[1]+n[1]),(v[0]-n[0],v[1]-n[1])],fill=col)
@lru_cache(1)
def states():return json.loads((A/'us-states.json').read_text())['features']
def render(lang,kind,p=1):
 T=lambda ru,en:ru if lang=='ru' else en
 direct={'doctor':('a',0,T('ВРАЧ ПРИШЁЛ К ДЕТЕКТИВАМ','A DOCTOR CAME TO POLICE')),'voice':('b',0,T('«МОЯ ЖЕНА ГОВОРИТ ИНЫМ ГОЛОСОМ»','“MY WIFE SPEAKS IN ANOTHER VOICE”')),'fire':('a',1,T('ПОЖАР В КВАРТИРЕ','FIRE IN HER APARTMENT')),'stalled':('a',3,T('СЛЕДСТВИЕ ЗАШЛО В ТУПИК','THE INVESTIGATION STALLED')),'remy':('b',0,T('РЕМИ ЧУА ВЕЛА СЕБЯ СТРАННО','REMIBIAS CHUA ACTED STRANGELY')),'voice2':('b',1,T('ПО СЛОВАМ ЕЁ МУЖА','ACCORDING TO HER HUSBAND')),'hesitated':('b',2,T('СУПРУГИ РЕШИЛИ РАССКАЗАТЬ','THE COUPLE DECIDED TO TELL POLICE')),'check':('b',3,T('ДЕТЕКТИВЫ ПРОВЕРЯЮТ ИМЯ','DETECTIVES CHECK THE NAME'))}
 if kind in direct:
  sheet,i,title=direct[kind];return shot(sheet,i,title)
 if kind=='teresita':return face('teresita',T('ТЕРЕСИТА БАСА','TERESITA BASA'))
 if kind=='showery':return face('allan',T('АЛЛАН ШОУЭРИ','ALLAN SHOWERY'),T('Работал в той же больнице','Worked at the same hospital'))
 if kind=='crime':return face('teresita',T('УБИЙСТВО И ПОЖАР','MURDER AND FIRE'),T('Квартиру пытались поджечь','The apartment was set on fire'))
 if kind=='jewelry_taken':return shot('c',0,T('УКРАШЕНИЯ ПОГИБШЕЙ','THE VICTIM’S JEWELRY'))
 if kind=='found':return shot('c',1,T('НАШЛИ У ДЕВУШКИ ШОУЭРИ','FOUND AT SHOWERY’S GIRLFRIEND’S'))
 if kind=='confession':return shot('c',2,T('ШОУЭРИ СНАЧАЛА ПРИЗНАЛСЯ','SHOWERY FIRST CONFESSED'))
 if kind=='guilty':return shot('c',3,T('ПОЗЖЕ ПРИЗНАЛ ВИНУ В СУДЕ','LATER HE PLEADED GUILTY'),T('14 лет заключения','Fourteen years in prison'))
 if kind=='question':return shot('b',1,T('ОТКУДА РЕМИ УЗНАЛА?','HOW DID REMIBIAS KNOW?'))
 if kind=='name_hook':
  im=base(T('ОНА НАЗВАЛА ИМЯ','SHE GAVE THEM A NAME'));place(im,gen('a',0),(0,340,1080,930));d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1050,1080,1340),fill=(7,16,26,210));txt(d,(540,1205),T('УБИЙЦА БЫЛ РЯДОМ?','WAS THE KILLER NEARBY?'),53,GOLD);return im
 if kind=='city':
  im=base(T('ЧИКАГО • 1977','CHICAGO • 1977'));d=ImageDraw.Draw(im);d.rounded_rectangle((75,390,1005,1120),25,fill='#203948',outline='#557482',width=3)
  def xy(lon,lat):return (100+(lon+94)/18*850,1050-(lat-36)/8*530)
  for f in states():
   if f['properties']['name'] not in ['Illinois','Indiana','Iowa','Missouri','Wisconsin','Michigan']:continue
   geom=f['geometry'];polys=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
   for poly in polys:
    ring=poly[0];pts=[xy(a,b) for a,b,*_ in ring];d.polygon(pts,fill=GOLD if f['properties']['name']=='Illinois' else '#456170',outline='#9dafb1')
  x,y=xy(-87.64,41.89);d.ellipse((x-19,y-19,x+19,y+19),fill=INK,outline=GOLD,width=4);arrow(d,[(x,y),(x,1210),(550,1210)],p,GOLD)
  badge(d,(160,1245,760,150),T('БОЛЬНИЦА И КВАРТИРА — ЧИКАГО','HOSPITAL AND APARTMENT — CHICAGO'),TEAL,36);return im
 if kind=='evidence':
  im=base(T('НАСТОЯЩАЯ УЛИКА','REAL PHYSICAL EVIDENCE'));place(im,gen('c',1),(0,345,1080,850));d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,1110,1080,1420),fill=(8,22,33,235));badge(d,(55,1150,455,205),T('ЖЕМЧУЖНОЕ\nКОЛЬЦО','PEARL\nRING'),GOLD,40)
  if p>.2:badge(d,(570,1150,455,205),T('НЕФРИТОВЫЙ\nКУЛОН','JADE\nPENDANT'),TEAL,40)
  return im
 if kind=='mistrial':
  im=base(T('ПЕРВЫЙ СУД — БЕЗ РЕШЕНИЯ','FIRST TRIAL — NO VERDICT'));place(im,archive('news'),(60,355,960,860));d=ImageDraw.Draw(im)
  badge(d,(95,1240,890,170),T('СУД ПРИСЯЖНЫХ: ТУПИК','THE JURY COULD NOT AGREE'),GOLD,40);return im
 if kind=='hospital':
  im=base(T('ОНИ РАБОТАЛИ В ОДНОЙ БОЛЬНИЦЕ','THEY WORKED AT THE SAME HOSPITAL'));d=ImageDraw.Draw(im)
  for k,(name,kind2,col) in enumerate([(T('ТЕРЕСИТА','TERESITA'),'teresita',GOLD),(T('РЕМИ','REMIBIAS'),None,TEAL),(T('АЛЛАН','ALLAN'),'allan',MUTE)]):
   x=40+k*350;pic=archive(kind2) if kind2 else gen('b',0);place(im,pic,(x,410,300,590));badge(d,(x,1010,300,110),name,col,31)
   arrow(d,[(x+150,1130),(x+150,1260),(540,1260)],max(0,min(1,p*2-k*.12)),col)
  txt(d,(540,1390),T('ВОЗМОЖНАЯ СВЯЗЬ — НЕ ДОКАЗАТЕЛЬСТВО','A POSSIBLE PATH OF INFORMATION'),32,GOLD);return im
 if kind=='unknown':
  im=base(T('ИСТОЧНИК СВЕДЕНИЙ НЕИЗВЕСТЕН','THE SOURCE OF THE TIP IS UNKNOWN'));place(im,gen('b',1),(0,370,1080,810));d=ImageDraw.Draw(im)
  badge(d,(90,1220,900,180),T('ЧТО ОНА ЗНАЛА — И КАК УЗНАЛА?','WHAT DID SHE KNOW — AND HOW?'),GOLD,36);return im
 if kind=='tip':
  im=base(T('РАССКАЗ ПРИВЁЛ К ПОДОЗРЕВАЕМОМУ','THE ACCOUNT LED TO A SUSPECT'));place(im,gen('b',2),(0,340,1080,930));d=ImageDraw.Draw(im)
  arrow(d,[(160,1340),(900,1340)],p,TEAL);return im
 if kind=='final':
  im=base(T('ДОКАЗАТЕЛЬСТВО — УКРАШЕНИЯ','THE JEWELRY WAS THE EVIDENCE'));place(im,archive('teresita'),(55,365,440,760));place(im,gen('c',1),(550,365,470,760));d=ImageDraw.Draw(im)
  arrow(d,[(470,1225),(610,1225)],p,GOLD);badge(d,(105,1280,870,140),T('КОЛЬЦО И КУЛОН ПОДТВЕРДИЛИ УЛИКУ','RING AND PENDANT VERIFIED THE LEAD'),GOLD,34);return im
 raise ValueError(kind)
