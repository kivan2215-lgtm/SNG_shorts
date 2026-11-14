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
@lru_cache(12)
def photo(name):return Image.open(A/(name+'.jpg')).convert('RGB')
@lru_cache(4)
def gen(i):
 im=photo('scenes_a') if (A/'scenes_a.jpg').exists() else Image.open(A/'scenes_a.png').convert('RGB');w,h=im.size;x=i%2;y=i//2
 return im.crop((x*w//2+4,y*h//2+4,(x+1)*w//2-4,(y+1)*h//2-4))
def badge(d,y,s,col=GOLD):
 d.rounded_rectangle((65,y,1015,y+130),18,fill='#213845',outline=col,width=2);txt(d,(540,y+65),s,40,col,w=900)
def archive(name,title,sub=''):
 im=base(title);place(im,photo(name),(0,370,1080,1000));d=ImageDraw.Draw(im)
 if sub:badge(d,1335,sub)
 return im
def arrow(d,points,p,col=GOLD):
 p=min(1,max(0,p));lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];left=p*sum(lengths);end=points[0];ang=0
 for a,b,l in zip(points,points[1:],lengths):
  if left<=0:break
  f=min(1,left/l);end=(a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1]));d.line((a,end),fill=col,width=7);left-=l;ang=math.atan2(b[1]-a[1],b[0]-a[0])
 if p:
  v=(end[0]-22*math.cos(ang),end[1]-22*math.sin(ang));n=(-11*math.sin(ang),11*math.cos(ang));d.polygon([end,(v[0]+n[0],v[1]+n[1]),(v[0]-n[0],v[1]-n[1])],fill=col)
def render(lang,k,p=1):
 T=lambda ru,en:ru if lang=='ru' else en
 if k=='court_hook':return archive('court',T('ОНА УКАЗАЛА НА ПОДСУДИМОГО','SHE POINTED AT THE DEFENDANT'),T('ФЛОРИДА • СУД • 1998','FLORIDA • COURT • 1998'))
 if k=='other_case':
  im=base(T('НО ЭТО БЫЛО ДРУГОЕ ДЕЛО','BUT THIS WAS A DIFFERENT CASE'));place(im,photo('court'),(0,340,1080,700));d=ImageDraw.Draw(im)
  badge(d,1130,T('ОНА ВЫЖИЛА','SHE SURVIVED'),TEAL)
  if p>.3:badge(d,1300,T('ДРУГАЯ ЖЕНЩИНА — НЕТ','ANOTHER WOMAN DID NOT'))
  return im
 if k=='rewind':
  im=base(T('ПОЧЕМУ ОНА СВИДЕТЕЛЬ?','WHY WAS SHE A WITNESS?'));place(im,photo('court'),(0,360,1080,700));d=ImageDraw.Draw(im)
  txt(d,(220,1210),'1998',65,INK);txt(d,(850,1210),'1978',65,GOLD);arrow(d,[(380,1210),(690,1210)],p);badge(d,1360,T('НА ДВАДЦАТЬ ЛЕТ НАЗАД','TWENTY YEARS EARLIER'));return im
 if k in ('road','isolated','ravine'):
  idx={'road':0,'isolated':1,'ravine':2}[k];titles={'road':T('КАЛИФОРНИЯ • 1978','CALIFORNIA • 1978'),'isolated':T('ОН УВЁЗ ЕЁ С ДОРОГИ','HE TOOK HER TO AN ISOLATED PLACE'),'ravine':T('ОН ОСТАВИЛ ЕЁ УМИРАТЬ','HE LEFT HER TO DIE')}
  im=base(titles[k]);place(im,gen(idx),(0,350,1080,1110));d=ImageDraw.Draw(im)
  if k=='road':badge(d,1330,T('МЭРИ ВИНСЕНТ • 15 ЛЕТ','MARY VINCENT • AGE 15'))
  return im
 if k=='singleton':return archive('singleton',T('ЛОУРЕНС СИНГЛТОН','LAWRENCE SINGLETON'))
 if k=='escape':
  im=base(T('МЭРИ ВЫБРАЛАСЬ К ЛЮДЯМ','MARY REACHED HELP'));place(im,gen(3),(0,345,1080,800));d=ImageDraw.Draw(im)
  labels=[T('ОВРАГ','RAVINE'),T('ДОРОГА','ROAD'),T('ПОМОЩЬ','HELP')]
  for i,s in enumerate(labels):
   x=70+i*335;y=1220;d.rounded_rectangle((x,y,x+270,y+120),16,fill='#203947',outline=TEAL if i==2 else GOLD,width=3);txt(d,(x+135,y+60),s,32,INK,w=245)
   if i<2:arrow(d,[(x+275,y+60),(x+325,y+60)],min(1,max(0,p*3-i)),GOLD)
  return im
 if k in ('sentence','release','served'):
  title={'sentence':T('ПРИГОВОР • 1979','SENTENCED • 1979'),'release':T('ОСВОБОЖДЁН • 1987','RELEASED • 1987'),'served':T('ОКОЛО ВОСЬМИ ЛЕТ','ABOUT EIGHT YEARS')}[k]
  im=base(title);place(im,photo('singleton'),(70,385,300,420));d=ImageDraw.Draw(im)
  txt(d,(730,505),'≈8' if k=='served' else '14',150,GOLD);txt(d,(730,655),T('ЛЕТ ОТБЫТО','YEARS SERVED') if k=='served' else T('ЛЕТ ПО ПРИГОВОРУ','YEAR SENTENCE'),35,INK,w=520)
  x,y,w=90,980,900
  d.rounded_rectangle((x,y,x+w,y+90),14,fill='#2c424d');d.rounded_rectangle((x,y,x+int(w*(1 if k=='sentence' else 8/14)*max(.02,p)),y+90),14,fill=GOLD)
  txt(d,(150,1120),'1979',37,INK);txt(d,(890,1120),T('14 ЛЕТ','14 YEARS'),37,INK)
  if k!='sentence':
   txt(d,(600,1225),T('1987: УСЛОВНО-ДОСРОЧНО','1987: RELEASED ON PAROLE'),38,TEAL)
   badge(d,1350,T('ОТБЫЛ ОКОЛО 8 ЛЕТ','SERVED ABOUT 8 YEARS'),TEAL)
  else:badge(d,1320,T('ЗА НАПАДЕНИЕ НА МЭРИ','FOR THE ATTACK ON MARY'))
  return im
 if k=='fear':return archive('mary1997',T('СТРАХ НЕ ЗАКОНЧИЛСЯ','THE FEAR DID NOT END'),T('МЭРИ С СЫНОМ • СНИМОК 1997 ГОДА','MARY WITH HER SON • PHOTO: 1997'))
 if k=='arrest':return archive('arrest1997',T('ФЛОРИДА • 1997 • НОВОЕ УБИЙСТВО','FLORIDA • 1997 • ANOTHER MURDER'),T('РОКСАНА ХЕЙС • 31 ГОД','ROXANNE HAYES • AGE 31'))
 if k=='witness':
  im=base(T('ОЧЕВИДЕЦ ПОЗВАЛ НА ПОМОЩЬ','A WITNESS WENT FOR HELP'));d=ImageDraw.Draw(im)
  d.rounded_rectangle((70,390,1010,1410),18,fill='#e9e3d5')
  txt(d,(540,520),'SINGLETON v. STATE',42,'#14232d');txt(d,(540,640),T('ВЕРХОВНЫЙ СУД ФЛОРИДЫ • 2001','FLORIDA SUPREME COURT • 2001'),28,'#40515c')
  txt(d,(540,860),'“an eyewitness”',55,'#14232d');txt(d,(540,1060),'Paul Hitson',50,'#14232d')
  txt(d,(540,1280),T('Раздел I: обстоятельства дела','Section I: facts of the case'),32,'#40515c');return im
 if k in ('court_return','identify'):
  im=archive('court',T('МЭРИ СНОВА ПЕРЕД НИМ','MARY FACED HIM AGAIN'),T('1998 • ДЕЛО ОБ УБИЙСТВЕ РОКСАНЫ','1998 • ROXANNE’S MURDER CASE'))
  if k=='identify':
   d=ImageDraw.Draw(im);txt(d,(540,1245),T('ОНА ОПОЗНАЛА ЕГО','SHE IDENTIFIED HIM'),42,TEAL)
  return im
 if k=='penalty':
  im=base(T('ЕЁ ПОКАЗАНИЯ ИМЕЛИ ЗНАЧЕНИЕ','HER TESTIMONY MATTERED'));place(im,photo('court'),(0,350,1080,760));d=ImageDraw.Draw(im)
  badge(d,1190,T('ВИНА УЖЕ УСТАНОВЛЕНА','GUILT ALREADY DETERMINED'),TEAL)
  if p>.3:badge(d,1360,T('РЕШАЕТСЯ НАКАЗАНИЕ','DETERMINING THE SENTENCE'))
  return im
 if k=='death_sentence':
  im=base(T('ПРИГОВОР: СМЕРТНАЯ КАЗНЬ','SENTENCE: DEATH'));d=ImageDraw.Draw(im)
  d.rounded_rectangle((70,390,1010,1410),18,fill='#e9e3d5')
  txt(d,(540,520),'SINGLETON v. STATE',44,'#14232d');txt(d,(540,720),'“we affirm the conviction\nand death sentence”',44,'#14232d',w=870)
  txt(d,(540,1000),T('Приговор подтверждён\nВерховным судом Флориды','Affirmed by the\nFlorida Supreme Court'),42,'#14232d');txt(d,(540,1280),'2001',52,'#40515c');return im
 if k=='twenty_years':
  im=base(T('ДВА ДЕЛА ОДНОГО ПРЕСТУПНИКА','TWO CASES. THE SAME ATTACKER.'));d=ImageDraw.Draw(im)
  place(im,photo('court'),(40,375,1000,650))
  badge(d,1100,T('1978 • МЭРИ ВИНСЕНТ','1978 • MARY VINCENT'),TEAL)
  arrow(d,[(540,1240),(540,1300)],p)
  badge(d,1320,T('1997 • РОКСАНА ХЕЙС','1997 • ROXANNE HAYES'));return im
 if k=='roxanne':
  im=base(T('РОКСАНА ХЕЙС','ROXANNE HAYES'));d=ImageDraw.Draw(im)
  txt(d,(540,650),'31',200,GOLD);txt(d,(540,840),T('ГОД','YEARS OLD'),54)
  txt(d,(540,1090),T('МАТЬ ТРОИХ ДЕТЕЙ','MOTHER OF THREE'),42,INK)
  badge(d,1325,'19.02.1997');return im
 if k=='comparison':
  im=base(T('ВАЖНАЯ ДЕТАЛЬ ХРОНОЛОГИИ','AN IMPORTANT TIMELINE DETAIL'));d=ImageDraw.Draw(im)
  badge(d,470,T('1979: ПРИГОВОР — 14 ЛЕТ','1979: SENTENCED TO 14 YEARS'))
  arrow(d,[(540,620),(540,900)],p,TEAL)
  badge(d,930,T('1997: УБИЙСТВО РОКСАНЫ','1997: ROXANNE’S MURDER'),TEAL)
  txt(d,(540,1210),T('МЕЖДУ НИМИ — ОКОЛО 18 ЛЕТ','ABOUT 18 YEARS BETWEEN THEM'),38,INK)
  txt(d,(540,1380),T('Полный срок закончился бы раньше','The full sentence would have ended earlier'),34,GOLD);return im
 if k=='final':return archive('advocacy1999',T('КАК ОЦЕНИТЬ РИСК ПОСЛЕ ОСВОБОЖДЕНИЯ?','HOW DO WE ASSESS THE RISK OF RELEASE?'),T('МЭРИ НА ВСТРЕЧЕ В ЗАЩИТУ ЖЕРТВ • 1999','MARY AT A VICTIMS’ RIGHTS EVENT • 1999'))
 raise ValueError(k)
