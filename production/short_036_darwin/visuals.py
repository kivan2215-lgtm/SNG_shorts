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
@lru_cache(16)
def art(sheet,index):
 im=Image.open(P/'assets'/f'scenes{sheet}.png').convert('RGB');w,h=im.size;im=im.crop((index%2*w//2,index//2*h//2,(index%2+1)*w//2,(index//2+1)*h//2))
 scale=min(1080/im.width,1440/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 out=Image.new('RGB',(1080,1920),BG);out.paste(im,((1080-im.width)//2,240+(1440-im.height)//2))
 overlay=Image.new('RGBA',out.size);d=ImageDraw.Draw(overlay)
 for y in range(230):d.line((0,1450+y,1080,1450+y),fill=(7,25,35,round(210*y/230)))
 return Image.alpha_composite(out.convert('RGBA'),overlay).convert('RGB')
@lru_cache(12)
def model(i=0,kind='passage'):
 f=P/'frames'/kind/f'{i:04d}.jpg'
 if not f.exists():f=P/'frames/passage'/f'probe_{min([0,22,45,68,90],key=lambda x:abs(x-i)):04d}.jpg'
 return Image.open(f).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
@lru_cache(10)
def photo(k):return Image.open(P/'assets'/f'{k}.jpg').convert('RGB')
def archive(k,box=(40,330,1040,1380)):
 out=Image.new('RGB',(1080,1920),BG);pic=photo(k);x,y,x1,y1=box;scale=min((x1-x)/pic.width,(y1-y)/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)),Image.Resampling.LANCZOS);out.paste(pic,(int((x+x1-pic.width)/2),int((y+y1-pic.height)/2)));return out
N={
'dead':('ЕГО СЧИТАЛИ ПОГИБШИМ','HE WAS PRESUMED DEAD'),
'arrival':('ОН ПРИШЁЛ В ПОЛИЦИЮ','HE WALKED INTO A POLICE STATION'),
'memory':('ОН ГОВОРИЛ О ПОТЕРЕ ПАМЯТИ','HE CLAIMED HE HAD LOST HIS MEMORY'),
'clue':('ОДНА ФОТОГРАФИЯ ИЗМЕНИЛА ВСЁ','ONE PHOTOGRAPH CHANGED EVERYTHING'),
'date':('АНГЛИЯ · 2002','ENGLAND · 2002'),
'kayak':('ДЖОН ДАРВИН ИСЧЕЗ В МОРЕ','JOHN DARWIN VANISHED AT SEA'),
'wreck':('НАШЛИ РАЗБИТУЮ БАЙДАРКУ','THE WRECKED KAYAK WAS FOUND'),
'missing':('НО ГДЕ САМ ДЖОН?','BUT WHERE WAS JOHN?'),
'declared':('ЕГО ПРИЗНАЛИ ПОГИБШИМ','HE WAS DECLARED DEAD'),
'payout':('СТРАХОВКА И ДРУГИЕ ВЫПЛАТЫ','INSURANCE AND OTHER PAYOUTS'),
'grief':('СЫНОВЬЯ ОПЛАКИВАЛИ ОТЦА','HIS SONS MOURNED THEIR FATHER'),
'return':('ДЕКАБРЬ 2007 · ВОЗВРАЩЕНИЕ','DECEMBER 2007 · HIS RETURN'),
'search':('ПОИСК В ИНТЕРНЕТЕ','AN ONLINE SEARCH'),
'photo':('ПОДЛИННЫЙ СНИМОК ИЗ ПАНАМЫ','THE ACTUAL PANAMA PHOTOGRAPH'),
'couple':('ДЖОН И ЕГО ЖЕНА','JOHN AND HIS WIFE'),
'dated':('СНИМОК СДЕЛАН В 2006 ГОДУ','THE PHOTO WAS TAKEN IN 2006'),
'contradiction':('НО ОН СЧИТАЛСЯ МЁРТВЫМ','BUT HE WAS SUPPOSED TO BE DEAD'),
'staged':('ГИБЕЛЬ БЫЛА ИНСЦЕНИРОВАНА','HE HAD STAGED HIS DEATH'),
'hiding':('ОН СКРЫВАЛСЯ РЯДОМ С СЕМЬЁЙ','HE HID CLOSE TO HIS FAMILY'),
'visitors':('КАК ОН ПРЯТАЛСЯ ОТ ГОСТЕЙ?','HOW DID HE HIDE FROM VISITORS?'),
'passage':('ПРОХОД ЗА ШКАФОМ','THE PASSAGE BEHIND THE WARDROBE'),
'knew':('ЖЕНА ВСЁ ЗНАЛА','HIS WIFE KNEW'),
'panama':('НОВАЯ ЖИЗНЬ В ПАНАМЕ','A NEW LIFE IN PANAMA'),
'website':('ФОТО ОКАЗАЛОСЬ НА САЙТЕ','THE PHOTO WENT ON A WEBSITE'),
'verdict':('2008 · ОБОИХ ОСУДИЛИ','2008 · BOTH WERE SENTENCED'),
'sentence':('БОЛЬШЕ ШЕСТИ ЛЕТ КАЖДОМУ','MORE THAN SIX YEARS EACH'),
'sons':('СЫНОВЬЯ НИЧЕГО НЕ ЗНАЛИ','THEIR SONS KNEW NOTHING'),
'newlife':('РОДИТЕЛИ СТРОИЛИ НОВУЮ ЖИЗНЬ','THEIR PARENTS PLANNED A NEW LIFE'),
'believed':('А СЫНОВЬЯ ВЕРИЛИ В ЕГО ГИБЕЛЬ','THE SONS BELIEVED HE WAS DEAD'),
'end':('ЧТО ТРУДНЕЕ ПРОСТИТЬ?','WHAT IS HARDER TO FORGIVE?')}
def head(d,s):
 d.rounded_rectangle((65,154,130,162),radius=4,fill=GOLD);text(d,(65,210),s,43,WHITE,'lm',950)
def timeline(d,tr,phase,sec):
 y=1270;xs=[170,540,900];years=['2002','2006','2007']
 for i,x in enumerate(xs):
  col=GOLD if i==phase else CYAN
  d.ellipse((x-10,y-10,x+10,y+10),fill=col);text(d,(x,y+55),years[i],42,col)
  if i<2:d.line((x+15,y,xs[i+1]-15,y),fill='#395762',width=4)
 if phase>=1:
  q=ease(sec/.9);d.line((xs[0],y,xs[0]+(xs[1]-xs[0])*q,y),fill=GOLD,width=7)
  text(d,(280,1140),tr('ДАТА НА ФОТО','DATE ON THE PHOTO'),33,GOLD,width=460)
 text(d,(170,1390),tr('ИСЧЕЗ','VANISHED'),30,CYAN,width=270);text(d,(900,1390),tr('ВЕРНУЛСЯ','RETURNED'),30,CYAN,width=280)
def search_interface(im,tr,seconds):
 # An illustrative interface using the reported query, never fabricated results.
 ui=Image.new('RGBA',(600,500),'#dce5e8');ud=ImageDraw.Draw(ui)
 ud.rectangle((0,0,600,65),fill='#234954');text(ud,(300,34),tr('ПОИСК','SEARCH'),40,WHITE)
 ud.rounded_rectangle((25,140,575,315),radius=14,fill='#ffffff',outline='#748d98',width=4)
 query='John Anne Panama';n=min(len(query),int(max(0,seconds)*18));typed=query[:n]
 # Two readable lines; no search results or likeness of a real browser screenshot.
 first=typed[:9];second=typed[10:]
 text(ud,(60,192),first,48,'#16313c','lm',480)
 text(ud,(60,260),second,48,'#16313c','lm',480)
 if n<len(query):
  yy=192 if n<=9 else 260;xx=60+font(48).getlength(first if n<=9 else second);ud.line((xx+5,yy-22,xx+5,yy+23),fill='#16313c',width=4)
 ud.ellipse((455,370,505,420),outline='#234954',width=7);ud.line((497,413,523,439),fill='#234954',width=7)
 # Perspective map stays inside the generated monitor glass, preserving its bezel.
 dst=[(462,736),(861,725),(849,1061),(455,1046)];src=[(0,0),(600,0),(600,500),(0,500)];A=[];B=[]
 for (x,y),(u,v) in zip(dst,src):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 coeff=np.linalg.solve(np.array(A,float),np.array(B,float));warped=ui.transform((1080,1920),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
 return Image.alpha_composite(im.convert('RGBA'),warped).convert('RGB')
def render(lang,k,p=0,seconds=None):
 tr=lambda a,b:b if lang=='en' else a;seconds=p*3 if seconds is None else seconds
 people={'arrival':(1,0),'memory':(1,1),'clue':(3,0),'date':(1,3),'kayak':(1,2),'wreck':(2,1),'declared':(2,1),'payout':(3,1),'grief':(2,2),'return':(2,0),'search':(2,3),'hiding':(3,2),'newlife':(3,3)}
 if k=='dead':
  im=Image.open(P/'assets/opening.png').convert('RGB');scale=min(1080/im.width,1920/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(1080,1920),BG);out.paste(im,((1080-im.width)//2,(1920-im.height)//2));im=out
 elif k in people:im=art(*people[k]).copy()
 elif k in ['dead','missing','staged']:im=archive('john',(40,480,1040,1120))
 elif k in ['dated','contradiction']:im=archive('panama',(40,300,1040,1000))
 elif k in ['photo','couple','website']:im=archive('panama',(40,320,1040,1120))
 elif k in ['knew','verdict','sentence']:im=archive('anne',(70,320,1010,1160))
 elif k in ['sons','believed','end']:im=archive('sons',(40,340,1040,1240))
 elif k=='panama':
  im=archive('farm',(40,350,1040,1050))
 elif k in ['visitors','passage']:
  im=model(0,'overview').copy() if k=='visitors' else model(min(90,round(seconds*30))).copy()
 else:raise ValueError(k)
 if k=='search':im=search_interface(im,tr,seconds)
 d=ImageDraw.Draw(im);head(d,tr(*N[k]))
 if k=='dead':
  tag(d,(540,1270),tr('5 ЛЕТ СЧИТАЛСЯ ПОГИБШИМ','PRESUMED DEAD FOR 5 YEARS'),GOLD,42)
 if k=='missing':tag(d,(540,1320),tr('ТЕЛО НЕ НАШЛИ','NO BODY WAS FOUND'),CYAN,42)
 if k=='declared':tag(d,(540,1330),tr('2003 · ПРИЗНАН ПОГИБШИМ','2003 · DECLARED DEAD'),GOLD,38)
 if k=='payout':tag(d,(540,1360),tr('ВЫПЛАТЫ ПОСЛЕ «СМЕРТИ»','PAYOUTS AFTER HIS “DEATH”'),GOLD,38)
 if k=='memory':tag(d,(540,1350),tr('ТАК ОН ОБЪЯСНЯЛ ИСЧЕЗНОВЕНИЕ','HIS EXPLANATION FOR DISAPPEARING'),CYAN,32)
 if k=='photo':tag(d,(540,1300),tr('ПАНАМА','PANAMA'),GOLD,48)
 if k=='couple':
  # Labels identify only John and Anne; third person is the property adviser.
  tag(d,(260,1260),tr('ДЖОН','JOHN'),GOLD,40);tag(d,(740,1260),tr('ЭНН · ЖЕНА','ANNE · HIS WIFE'),CYAN,37)
  arrow(d,(260,1200),(260,1100),GOLD);arrow(d,(740,1200),(490,1100),CYAN)
 if k in ['dated','contradiction']:
  src=photo('panama');detail=src.crop((int(src.width*.70),int(src.height*.82),src.width,src.height));scale=400/detail.width;detail=detail.resize((400,round(detail.height*scale)),Image.Resampling.LANCZOS);im.paste(detail,(600,1030));d=ImageDraw.Draw(im);d.rounded_rectangle((596,1026,1004,1034+detail.height),radius=5,outline=GOLD,width=3);timeline(d,tr,1,seconds)
 if k=='contradiction':tag(d,(540,360),tr('«ПОГИБ» В 2002','“DIED” IN 2002'),RED,38)
 if k=='staged':tag(d,(540,1320),tr('ЭТО БЫЛ ОБМАН','IT WAS A DECEPTION'),RED,45)
 if k in ['visitors','passage']:
  tag(d,(540,330),tr('УСЛОВНЫЙ РАЗРЕЗ','SCHEMATIC CUTAWAY'),CYAN,32)
  # The labels preserve spatial orientation throughout the movement.
  tag(d,(270,1220),tr('СЕМЕЙНОЕ\nЖИЛЬЁ','FAMILY\nHOME'),GOLD,34)
  tag(d,(760,510),tr('СОСЕДНЕЕ\nПОМЕЩЕНИЕ','ADJOINING\nPROPERTY'),CYAN,32)
  if k=='passage':
   tag(d,(760,1320),tr('ПРОХОД\nЗА ШКАФОМ','PASSAGE BEHIND\nTHE WARDROBE'),GREEN,32)
   arrow(d,(680,1250),(510,1110),GREEN,4)
 if k=='panama':tag(d,(540,1280),tr('ДЖОН В ПАНАМЕ · 2007','JOHN IN PANAMA · 2007'),GOLD,39)
 if k=='website':tag(d,(540,1280),'MOVE TO PANAMA',CYAN,43)
 if k=='sentence':
  tag(d,(540,1240),tr('ДЖОН — 6 ЛЕТ 3 МЕСЯЦА','JOHN — 6 YEARS 3 MONTHS'),GOLD,36)
  tag(d,(540,1360),tr('ЭНН — 6 ЛЕТ 6 МЕСЯЦЕВ','ANNE — 6 YEARS 6 MONTHS'),CYAN,36)
 if k=='sons':tag(d,(540,1340),tr('НЕ УЧАСТВОВАЛИ В ОБМАНЕ','THEY WERE NOT PART OF THE SCAM'),GOLD,37)
 if k=='end':
  tag(d,(540,1340),tr('ДЕНЬГИ ИЛИ ГОДЫ ГОРЯ?','MONEY OR YEARS OF GRIEF?'),GOLD,38)
 return im
