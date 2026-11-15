from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
import math,json
P=Path(__file__).parent
BG='#091722';WHITE='#f3f0e7';GOLD='#ffd080';CYAN='#79d9e4';RED='#ff8b80';GREEN='#96e4b4'
@lru_cache(100)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',n)
def text(d,xy,s,size=42,fill=WHITE,anchor='mm',width=920):
 lines=s.split('\n')
 while max(font(size).getlength(x) for x in lines)>width and size>22:size-=1
 for i,l in enumerate(lines):d.text((xy[0],xy[1]+(i-(len(lines)-1)/2)*(size+12)),l,font=font(size),fill=fill,anchor=anchor)
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def tag(d,xy,s,col=GOLD,size=32):
 lines=s.split('\n');w=min(1000,max(font(size).getlength(x) for x in lines)+30);h=len(lines)*(size+10)+16;x,y=xy
 d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=13,fill=BG,outline='#48606a',width=2);text(d,xy,s,size,col,width=w-25)
def arrow(d,a,b,col=CYAN,width=4):
 d.line([a,b],fill=col,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-17*math.cos(ang-.45),b[1]-17*math.sin(ang-.45)),(b[0]-17*math.cos(ang+.45),b[1]-17*math.sin(ang+.45))],fill=col)
def lead(d,xy,pt,s,col=GOLD):
 x,y=xy;px,py=pt;dy=35 if py>y else -35;d.line([(x,y+dy),(x,py),pt],fill=col,width=3);d.ellipse((px-7,py-7,px+7,py+7),outline=col,width=3);tag(d,xy,s,col)
@lru_cache(45)
def model(k,i=0):return Image.open(P/'frames'/k/f'{i:04d}.jpg').convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
@lru_cache(20)
def anchors(k):return json.loads((P/'frames'/k/'index.json').read_text())['anchors']
@lru_cache(2)
def portrait():return Image.open(P/'assets/doctor.jpg').convert('RGB')
def head(d,s,sub=''):
 d.rounded_rectangle((64,164,120,172),radius=3,fill=GOLD);text(d,(65,224),s,45,WHITE,'lm',930)
 if sub:text(d,(65,296),sub,30,CYAN,'lm',930)
NAMES={
'accuse':('ОНА НАЗВАЛА ВРАЧА','SHE ACCUSED HER DOCTOR'),
'first':('ДНК НЕ СОВПАЛА','THE DNA DID NOT MATCH'),
'double':('ДВЕ ПРОВЕРКИ. ТОТ ЖЕ РЕЗУЛЬТАТ.','TWO TESTS. THE SAME RESULT.'),
'doubt':('ОНА ОШИБЛАСЬ?','WAS SHE WRONG?'),
'promise':('ТАЙНА — ПОД КОЖЕЙ','THE SECRET WAS UNDER HIS SKIN'),
'date':('КАНАДА · 1992','CANADA · 1992'),
'patient':('ЗАЯВЛЕНИЕ ПАЦИЕНТКИ','THE PATIENT’S ALLEGATION'),
'blood':('УЛИКИ И ОБРАЗЕЦ КРОВИ','EVIDENCE AND A BLOOD SAMPLE'),
'negative':('СОВПАДЕНИЯ НЕТ','NO MATCH'),
'retest':('ОНА ДОБИЛАСЬ ПОВТОРНОЙ ПРОВЕРКИ','SHE DEMANDED ANOTHER TEST'),
'same':('РЕЗУЛЬТАТ НЕ ИЗМЕНИЛСЯ','THE RESULT DID NOT CHANGE'),
'closed':('ДЕЛО ЗАКРЫЛИ','THE CASE WAS CLOSED'),
'persist':('НО ОНА НЕ ОТСТУПИЛА','SHE REFUSED TO GIVE UP'),
'car':('НОВАЯ УЛИКА — ИЗ МАШИНЫ','A NEW CLUE FROM HIS CAR'),
'balm':('НА БАЛЬЗАМЕ ОСТАЛАСЬ СЛЮНА','SALIVA ON THE LIP BALM'),
'match':('ТЕПЕРЬ ДНК СОВПАЛА','THIS TIME, THE DNA MATCHED'),
'contradiction':('ОДИН ЧЕЛОВЕК. ДВА РЕЗУЛЬТАТА.','ONE MAN. TWO DIFFERENT RESULTS.'),
'second':('ПОЯВИЛАСЬ ЕЩЁ ОДНА ПОСТРАДАВШАЯ','ANOTHER VICTIM CAME FORWARD'),
'reopen':('РАССЛЕДОВАНИЕ ВОЗОБНОВИЛИ','THE INVESTIGATION REOPENED'),
'hair':('НОВЫЕ ОБРАЗЦЫ ПОДТВЕРДИЛИ СВЯЗЬ','NEW SAMPLES LINKED HIM TO THE CRIME'),
'court':('РАЗГАДКА ПРОЗВУЧАЛА НА СУДЕ','THE ANSWER EMERGED AT TRIAL'),
'tube':('ПОД КОЖЕЙ БЫЛА ТРУБКА','A TUBE BENEATH HIS SKIN'),
'foreign':('В НЕЙ БЫЛА ЧУЖАЯ КРОВЬ','IT CONTAINED SOMEONE ELSE’S BLOOD'),
'draw':('ОБРАЗЕЦ БРАЛИ ИЗ ТРУБКИ','THE SAMPLE CAME FROM THE TUBE'),
'switch':('ПОДМЕНИЛИ САМ ОБРАЗЕЦ','THE SAMPLE ITSELF WAS SWITCHED'),
'verdict':('1999 · ОБВИНИТЕЛЬНЫЙ ПРИГОВОР','1999 · CONVICTED'),
'sentence':('ШЕСТЬ ЛЕТ ТЮРЬМЫ','SIX YEARS IN PRISON'),
'seven':('СЕМЬ ЛЕТ БОРЬБЫ ЗА ПРАВОСУДИЕ','SEVEN YEARS FIGHTING FOR JUSTICE'),
'question':('ДОСТАТОЧНО ЛИ ШЕСТИ ЛЕТ?','IS SIX YEARS ENOUGH?')}
MAP={'first':'lab_close','double':'lab_close','doubt':'lab_close','promise':'arm_closed','patient':'clinic','blood':'lab','negative':'lab_close','retest':'folder','same':'lab_close','closed':'folder_motion','persist':'folder','car':'car','balm':'balm','match':'lab','contradiction':'lab','second':'folder','reopen':'folder_motion','hair':'hair','court':'court','tube':'arm_open','foreign':'arm_open','draw':'arm_open','switch':'arm_open','question':'court','seven':'court'}
def base_render(lang,k,p=0,seconds=None):
 en=lang=='en';tr=lambda a,b:b if en else a;seconds=p*2 if seconds is None else seconds
 if k in MAP:
  m=MAP[k];i=0
  if m=='folder_motion':
   i=min(30,round(seconds*30));i=30-i if k=='reopen' else i
  im=model(m,i).copy();a=anchors(m)
 else:im=Image.new('RGB',(1080,1920),BG);a={}
 d=ImageDraw.Draw(im);head(d,tr(*NAMES[k]))
 if k in ['accuse','sentence']:
  pic=portrait().resize((430,482),Image.Resampling.LANCZOS);im.paste(pic,(325,560));d=ImageDraw.Draw(im)
  text(d,(540,1120),tr('ДЖОН ШНЕЕБЕРГЕР','JOHN SCHNEEBERGER'),42)
  text(d,(540,1185),tr('ВРАЧ · КИПЛИНГ, САСКАЧЕВАН','PHYSICIAN · KIPLING, SASKATCHEWAN'),29,CYAN)
  if k=='accuse':tag(d,(540,420),tr('ЕЁ СЛОВА ПРОТИВ АНАЛИЗА','HER ACCOUNT VS. THE TEST'))
  else:tag(d,(540,410),tr('ПРИГОВОР: 6 ЛЕТ','SENTENCE: 6 YEARS'),RED,47)
 if k=='patient':
  lead(d,(540,420),a['couch'],tr('ВРАЧЕБНЫЙ КАБИНЕТ','EXAMINATION ROOM'),CYAN)
  tag(d,(540,1300),tr('ЕЁ ПОКАЗАНИЯ','HER ACCOUNT') if k!='second' else tr('НОВОЕ ЗАЯВЛЕНИЕ','ANOTHER ALLEGATION'))
 if k=='date':
  geo=json.loads((P/'assets/canada.geojson').read_text())['geometry'];polys=geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]
  def mp(lon,lat):return (100+(lon+141)/89*870,1190-(lat-41)/43*640)
  for depth in range(18,0,-2):
   for poly in polys:d.polygon([(mp(x,y)[0],mp(x,y)[1]+depth) for x,y in poly[0]],fill='#263e4d')
  for poly in polys:d.polygon([mp(x,y) for x,y in poly[0]],fill='#658b9a',outline='#a0bec6',width=2)
  pt=mp(-102.63,50.1);r=13+5*math.sin(seconds*3)
  d.ellipse((pt[0]-r,pt[1]-r,pt[0]+r,pt[1]+r),outline=GOLD,width=3);d.ellipse((pt[0]-6,pt[1]-6,pt[0]+6,pt[1]+6),fill=GOLD)
  lead(d,(540,1320),pt,tr('КИПЛИНГ · САСКАЧЕВАН','KIPLING · SASKATCHEWAN'))
 if k in ['first','double','negative','same','match','blood','doubt','contradiction']:
  # These are explanatory result summaries, not fabricated lab printouts or DNA profiles.
  yes=k=='match';col=GREEN if yes else RED
  left=(260,400);right=(800,400)
  tag(d,left,tr('УЛИКИ','EVIDENCE'),CYAN,30);tag(d,right,tr('СЛЮНА','SALIVA') if yes else tr('ОБРАЗЕЦ КРОВИ','BLOOD SAMPLE'),GOLD,28)
  for pt,x in [(a['sampleA'],260),(a['sampleB'],800)]:arrow(d,(x,450),pt,CYAN,3)
  result=tr('СОВПАЛО','MATCH') if yes else tr('НЕ СОВПАЛО','NO MATCH')
  if k=='blood':result=tr('СРАВНЕНИЕ ДНК','DNA COMPARISON');col=CYAN
  if k=='doubt':result=tr('КОМУ ВЕРИТЬ?','WHO WAS RIGHT?');col=GOLD
  tag(d,(540,1260),result,col,44)
  if k in ['double','same']:
   for j in range(2):tag(d,(320+j*440,1350),tr(f'ТЕСТ {j+1} — НЕТ',f'TEST {j+1} — NO MATCH'),RED,27)
  if k=='contradiction':
   d.rounded_rectangle((100,1190,980,1395),radius=15,fill=BG,outline='#425c69',width=2)
   text(d,(540,1245),tr('КРОВЬ → НЕ СОВПАЛО','BLOOD → NO MATCH'),34,RED)
   text(d,(540,1335),tr('СЛЮНА → СОВПАЛО','SALIVA → MATCH'),34,GREEN)
  # A quiet moving scan on the actual modeled instrument, with no invented numeric data.
  pt=a['screen'];r=24;ang=seconds*2.2
  d.arc((pt[0]-r,pt[1]-r,pt[0]+r,pt[1]+r),math.degrees(ang),math.degrees(ang)+250,fill=col,width=4)
 if k=='promise':
  lead(d,(540,470),a['arm'],tr('ЧТО ОН СКРЫВАЛ?','WHAT WAS HE HIDING?'),GOLD)
 if k in ['retest','closed','persist','reopen']:
  label={'retest':tr('ПОВТОРНАЯ ПРОВЕРКА','RETEST REQUESTED'),'closed':tr('1994 · ДЕЛО ЗАКРЫТО','1994 · CASE CLOSED'),'persist':tr('ПОИСК НОВОЙ УЛИКИ','SEARCHING FOR NEW EVIDENCE'),'reopen':tr('НОВЫЕ ПОКАЗАНИЯ → НОВАЯ ПРОВЕРКА','NEW ALLEGATION → NEW TESTS')}[k]
  tag(d,(540,1250),label,RED if k=='closed' else GOLD,33)
 if k=='second':
  lead(d,(540,440),a['file'],tr('НОВОЕ ЗАЯВЛЕНИЕ','ANOTHER ALLEGATION'),GOLD)
  tag(d,(540,1280),tr('ДРУГАЯ ПОСТРАДАВШАЯ','ANOTHER VICTIM'),CYAN,34)
 if k=='car':
  if p>.28:lead(d,(540,430),a['balm'],tr('БАЛЬЗАМ ДЛЯ ГУБ','LIP BALM'),GOLD)
 if k=='balm':
  lead(d,(540,430),a['balm'],tr('СЛЕДЫ СЛЮНЫ','TRACES OF SALIVA'),CYAN)
  q=ease(min(seconds/1.4,1));pt=a['balm'];end=(820,1280);now=(pt[0]+(end[0]-pt[0])*q,pt[1]+(end[1]-pt[1])*q);arrow(d,pt,now,CYAN)
  if p>.35:tag(d,(700,1340),tr('НОВЫЙ ИСТОЧНИК ДНК','A NEW DNA SOURCE'),CYAN,31)
 if k=='hair':
  lead(d,(340,440),a['hair'],tr('ВОЛОСЫ','HAIR'),GOLD);lead(d,(815,500),a['sample'],tr('НОВЫЕ ОБРАЗЦЫ','NEW SAMPLES'),CYAN)
  tag(d,(540,1310),tr('СВЯЗЬ ПОДТВЕРДИЛАСЬ','THE LINK WAS CONFIRMED'),GREEN,35)
 if k=='court':tag(d,(540,410),tr('1999 · РЕДЖАЙНА','1999 · REGINA'),GOLD)
 if k in ['tube','foreign','draw','switch']:
  # Topic-specific 3D model; no surgical method, measurements or needle insertion shown.
  pt=a['tube'];lead(d,(540,440),pt,tr('СКРЫТАЯ ТРУБКА','A CONCEALED TUBE'),GOLD)
  label=tr('ЧУЖАЯ КРОВЬ','SOMEONE ELSE’S BLOOD')
  if k=='tube':label=tr('ОБЪЯСНЕНИЕ НЕСОВПАДЕНИЙ','WHY THE RESULTS DIFFERED')
  tag(d,(540,1240),label,RED,38)
  if k in ['draw','switch']:
   end=(800,1160);q=ease(min(seconds/1.2,1));pos=(pt[0]+(end[0]-pt[0])*q,pt[1]+(end[1]-pt[1])*q);arrow(d,pt,pos,RED)
   d.rounded_rectangle((820,1100,885,1200),radius=13,fill='#c2d2d4',outline=WHITE,width=3)
   d.rounded_rectangle((828,1125,877,1190),radius=9,fill='#8c2e35')
   d.rectangle((817,1095,888,1114),fill=GOLD)
   tag(d,(550,1360),tr('В АНАЛИЗ ПОПАЛ НЕ ЕГО ОБРАЗЕЦ','THE TEST RECEIVED SOMEONE ELSE’S SAMPLE'),GOLD,29)
 if k=='verdict':
  d.rounded_rectangle((80,450,1000,1300),radius=20,fill='#e7e2d5');text(d,(540,515),'CBC NEWS · 27 NOV 1999',29,'#1a3442')
  text(d,(540,670),tr('ВРАЧ ПРИГОВОРЁН\nЗА СЕКСУАЛЬНОЕ НАСИЛИЕ','SASK. DOCTOR\nSENTENCED FOR RAPE'),42,'#172732',width=820)
  text(d,(540,900),tr('СУД ПРИЗНАЛ ЕГО ВИНОВНЫМ.\nНАСИЛИЕ И ПРЕПЯТСТВОВАНИЕ\nПРАВОСУДИЮ.','FOUND GUILTY.\nSEXUAL ASSAULT AND\nOBSTRUCTION OF JUSTICE.'),32,'#283c45',width=820)
  text(d,(540,1160),tr('СООБЩЕНИЕ О ПРИГОВОРЕ','REPORT ON THE SENTENCE'),27,'#425760')
 if k=='seven':
  d.rounded_rectangle((80,365,1000,650),radius=18,fill=BG,outline='#45606a',width=2)
  arrow(d,(180,520),(900,520),GOLD,5)
  for i in range(8):
   x=180+i*100;d.ellipse((x-6,514,x+6,526),fill=GOLD if i/7<=p else '#49616b')
  text(d,(180,580),'1992',32);text(d,(880,580),'1999',32);text(d,(540,430),tr('7 ЛЕТ ДО ПРИГОВОРА','7 YEARS TO A CONVICTION'),35,GOLD)
 if k=='question':
  tag(d,(540,410),tr('6 ЛЕТ — ДОСТАТОЧНО?','IS 6 YEARS ENOUGH?'),GOLD,47)
 return im

# V2: people-led illustrations, then explanatory models. No invented archival portraits.
@lru_cache(4)
def human_scene(index):
 sheet=Image.open(P/'assets/people_sheet.png').convert('RGB');w,h=sheet.size
 pic=sheet.crop((index%2*w//2,index//2*h//2,(index%2+1)*w//2,(index//2+1)*h//2))
 # Preserve both people and hands: full panel width, rather than aggressive vertical cropping.
 pic=pic.resize((1080,1440),Image.Resampling.LANCZOS)
 out=Image.new('RGB',(1080,1920),BG);out.paste(pic,(0,300))
 shade=Image.new('RGBA',out.size);sd=ImageDraw.Draw(shade)
 for y in range(300):
  sd.line((0,300+y,1080,300+y),fill=(9,23,34,round(150*(1-y/300))))
 for y in range(350):
  sd.line((0,1390+y,1080,1390+y),fill=(9,23,34,round(230*y/350)))
 return Image.alpha_composite(out.convert('RGBA'),shade).convert('RGB')

def render(lang,k,p=0,seconds=None):
 seconds=p*2 if seconds is None else seconds
 tr=lambda a,b:b if lang=='en' else a
 # Each people shot is followed by a close view explaining the relevant object.
 human={'patient':(0,2.6),'blood':(1,1.55),'retest':(1,1.65),'persist':(3,9),'car':(2,1.9)}
 if k in human and seconds<human[k][1]:
  im=human_scene(human[k][0]).copy();d=ImageDraw.Draw(im);head(d,tr(*NAMES[k]))
  if k=='car':tag(d,(540,1335),tr('ПОИСК СЛЕДОВ ДНК','SEARCHING FOR DNA TRACES'),CYAN,34)
  if k=='persist':tag(d,(540,1335),tr('ОНА ПРОДОЛЖИЛА ПОИСК','SHE KEPT SEARCHING'),GOLD,34)
  return im
 im=base_render(lang,k,p,seconds);d=ImageDraw.Draw(im)
 # Moving evidence path: source -> analysis -> finding, no fictional DNA sequence.
 if k in ['blood','first','negative','same','match','contradiction']:
  col=GREEN if k=='match' else CYAN
  points=[(220,1100),(540,1150),(860,1100)]
  d.line(points,fill='#385666',width=5)
  for j in range(3):
   q=(seconds*.45+j/3)%1;seg=min(1,int(q*2));u=q*2-seg
   a,b=points[seg],points[seg+1];x=a[0]+(b[0]-a[0])*u;y=a[1]+(b[1]-a[1])*u
   d.ellipse((x-7,y-7,x+7,y+7),fill=col)
  for x,y in points:d.ellipse((x-12,y-12,x+12,y+12),outline=col,width=3)
 if k=='tube' and seconds<1.4:
  # Gradual cutaway reveal, not a jump or an instructional surgery sequence.
  closed=model('arm_closed').copy();mask=Image.new('L',(1080,1920),0);md=ImageDraw.Draw(mask)
  y=620+650*ease(seconds/1.4);md.rectangle((0,0,1080,y),fill=255)
  im=Image.composite(im,closed,mask);d=ImageDraw.Draw(im);head(d,tr(*NAMES[k]))
 if k in ['draw','switch']:
  a=anchors('arm_open')['tube'];b=(800,1160)
  for j in range(4):
   q=(seconds*.38+j/4)%1;x=a[0]+(b[0]-a[0])*q;y=a[1]+(b[1]-a[1])*q
   d.ellipse((x-6,y-6,x+6,y+6),fill=RED)
 return im
