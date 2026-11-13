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
import subprocess
VIDEO_STARTS={'v_intro':1260,'v_confused':1270,'v_face':1280,'v_room':1288,'v_explain':1215,'v_listen':1340,'v_help':1500,'v_survived':1470,'v_after':1380,'v_final':1294,'v_dialogue':1304}
@lru_cache(30)
def frame(kind):
 b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(VIDEO_STARTS[kind]),'-i',str(A/'interrogation_source.mp4'),'-frames:v','1','-vf','crop=640:480:107:0,scale=1080:810','-f','rawvideo','-pix_fmt','rgb24','-'])
 return Image.frombytes('RGB',(1080,810),b)
@lru_cache(4)
def gen(i):
 im=Image.open(A/'scenes_a.png').convert('RGB');w,h=im.size;x=i%2;y=i//2
 return im.crop((x*w//2+4,y*h//2+4,(x+1)*w//2-4,(y+1)*h//2-4))
def badge(d,y,s,col=GOLD):
 d.rounded_rectangle((70,y,1010,y+125),20,fill='#203644',outline=col,width=2);txt(d,(540,y+62),s,36,col,w=890)
def render(lang,kind,p=1):
 T=lambda ru,en:ru if lang=='ru' else en
 if kind.startswith('v_'):
  titles={'v_intro':T('ДОПРОС РАНЕНОГО','QUESTIONING AN INJURED MAN'),'v_confused':T('ОН НЕ ПОНИМАЛ ВОПРОСЫ','HE STRUGGLED TO ANSWER'),'v_face':T('ТРАВМА ЛИЦА','A SEVERE FACIAL INJURY'),'v_room':T('ПОМОЩЬ ОТКЛАДЫВАЛАСЬ','TREATMENT WAS DELAYED'),'v_explain':T('ОН НАЗВАЛ НАПАДАВШИХ','HE IDENTIFIED HIS ATTACKERS'),'v_listen':T('РАНЕНИЕ НЕ РАСПОЗНАЛИ','THE WOUND WENT UNRECOGNIZED'),'v_help':T('ВЫЗВАЛИ МЕДИКОВ','PARAMEDICS WERE CALLED'),'v_survived':T('РАЙАН ВЫЖИЛ','RYAN SURVIVED'),'v_after':T('ПОСЛЕДСТВИЯ ОСТАЛИСЬ','THE INJURY CHANGED HIS LIFE'),'v_final':T('ПОЧЕМУ НЕ ПОМОГЛИ СРАЗУ?','WHY WAS TREATMENT DELAYED?'),'v_dialogue':T('ФРАГМЕНТ ДОПРОСА','INTERROGATION EXCERPT')}
  im=base(titles[kind]);im.paste(frame(kind),(0,430));d=ImageDraw.Draw(im)
  txt(d,(540,1340),T('РАЙАН УОЛЛЕР • ДЕКАБРЬ 2006','RYAN WALLER • DECEMBER 2006'),33,MUTE)
  return im
 if kind in ('medical','head_hook'):
  im=base(T('ФРАГМЕНТ ПУЛИ В МОЗГЕ','A BULLET FRAGMENT IN HIS BRAIN'));place(im,gen(2),(0,340,1080,860));d=ImageDraw.Draw(im)
  if kind=='medical':
   x,y=565,720;d.ellipse((x-16,y-16,x+16,y+16),fill=GOLD)
   endx=565+int(300*min(1,p*2));d.line((x,y,endx,y),fill=GOLD,width=5)
   badge(d,1205,T('ЛЕВАЯ ВИСОЧНАЯ ДОЛЯ','LEFT TEMPORAL LOBE'))
   if p>.35:txt(d,(540,1400),T('За левым глазом, перед ухом','Behind the left eye, in front of the ear'),35,INK)
  else:badge(d,1230,T('ОН НУЖДАЛСЯ В ПОМОЩИ','HE NEEDED MEDICAL HELP'))
  return im
 if kind in ('house','family','surgery'):
  i={'house':0,'family':1,'surgery':3}[kind];title={'house':T('АРИЗОНА • РОЖДЕСТВО 2006','ARIZONA • CHRISTMAS 2006'),'family':T('ОН НЕ ПРИШЁЛ К РОДИТЕЛЯМ','HE NEVER CAME HOME'),'surgery':T('ЭКСТРЕННАЯ ОПЕРАЦИЯ','EMERGENCY SURGERY')}[kind]
  im=base(title);place(im,gen(i),(0,380,1080,1050));return im
 if kind=='heather':
  im=base(T('ХИЗЕР КУАН','HEATHER QUAN'));place(im,Image.open(A/'heather.jpg').convert('RGB'),(80,355,920,1080));return im
 if kind=='document':
  im=base(T('ЧТО УСТАНОВИЛ СУД','WHAT THE COURT RECORD SAYS'));d=ImageDraw.Draw(im)
  d.rounded_rectangle((70,390,1010,1390),20,fill='#e5dfd0')
  txt(d,(540,500),'STATE v. CARVER',48,'#18232d')
  txt(d,(540,590),T('АПЕЛЛЯЦИОННЫЙ СУД АРИЗОНЫ','ARIZONA COURT OF APPEALS'),30,'#46515a')
  txt(d,(540,800),'“disoriented\nand confused”',56,'#18232d')
  txt(d,(540,1030),T('Растерянность и\nспутанность сознания','Confusion was recorded\nin the court decision'),42,'#18232d')
  txt(d,(540,1260),'2013 • ¶4',36,'#46515a');return im
 if kind=='dates':
  im=base(T('ДВА ДНЯ ДО ПОМОЩИ','TWO DAYS BEFORE HELP'));d=ImageDraw.Draw(im)
  for i,(date,ru,en) in enumerate([('23.12.2006','НАПАДЕНИЕ','THE ATTACK'),('25.12.2006','ПОЛИЦИЯ НАХОДИТ РАЙАНА','POLICE FIND RYAN')]):
   y=460+i*490;d.ellipse((120,y+30,160,y+70),fill=GOLD)
   txt(d,(610,y+50),date,66,GOLD);txt(d,(610,y+165),T(ru,en),37,INK,w=780)
  d.line((140,530,140,530+int(450*min(1,p*2))),fill=GOLD,width=7)
  badge(d,1290,T('23 → 25 ДЕКАБРЯ','DECEMBER 23 → 25'));return im
 if kind=='conviction':
  im=base(T('НАСТОЯЩИЕ ПРЕСТУПНИКИ','THE ACTUAL ATTACKERS'));place(im,Image.open(A/'richie.jpg').convert('RGB'),(70,400,400,560));d=ImageDraw.Draw(im)
  txt(d,(760,540),T('РИЧИ\nКАРВЕР','RICHIE\nCARVER'),48,GOLD,w=430)
  txt(d,(760,770),T('ЕГО ОТЕЦ\nЛАРРИ КАРВЕР','HIS FATHER\nLARRY CARVER'),37,INK,w=430)
  badge(d,1100,T('ОБА ОСУЖДЕНЫ','BOTH CONVICTED'))
  txt(d,(540,1340),T('ПРОКУРАТУРА ОКРУГА МАРИКОПА','MARICOPA COUNTY ATTORNEY'),30,MUTE);return im
 if kind=='death':
  im=base(T('РАЙАН УОЛЛЕР','RYAN WALLER'));pic=frame('v_after');place(im,pic,(0,380,1080,810));d=ImageDraw.Draw(im);badge(d,1240,'20.01.2016');return im
 raise ValueError(kind)
