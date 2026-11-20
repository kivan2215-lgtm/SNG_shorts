from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageOps
import math
W,H=720,1280
navy='#12292e'; cream='#f7edd4'; teal='#77c1b5'; red='#9a303e'
names='hot desk producer makeup host eyes answer monitor control hiring camera outside'.split()
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 if k=='centre':return Image.open('centre.jpg').convert('RGB')
 i=names.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB');w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+4,i//3*h+4,(i%3+1)*w-4,(i//3+1)*h-4))
@lru_cache(None)
def fit(k,w,h):
 return ImageOps.fit(panel(k),(w,h),centering=(.51,.42))
def put(d,xy,s,n,fill=cream):d.text(xy,s,font=font(n),fill=fill)
@lru_cache(None)
def scene(k,ru):
 pairs={'desk':'hot','host':'hot','makeup':'camera','producer':'desk','monitor':'answer','hiring':'outside','control':'eyes','centre':'desk'}
 if k not in pairs:return fit(k,W,H)
 im=Image.new('RGB',(W,H),navy);im.paste(fit(k,W,802),(0,0));im.paste(fit(pairs[k],W,468),(0,812))
 if k=='centre':
  d=ImageDraw.Draw(im);d.rectangle((17,711,483,792),fill=navy);put(d,(30,719),'Лондон · Television Centre' if ru else 'London · Television Centre',32);put(d,(32,758),'Panhard · 2009 · CC BY 2.5',20)
 return im
animated={'names','check','soul','split','resume','redlight','wait'}
def ease(t):return t*t*(3-2*t)
def draw(k,t,ru):
 word=lambda a,b:a if ru else b
 if k not in animated:return scene(k,ru)
 if k=='redlight':
  im=fit('camera',W,H).copy();d=ImageDraw.Draw(im);d.rounded_rectangle((44,700,326,782),10,fill=navy);col=red if t<.27 else '#f05355';d.ellipse((63,728,88,753),fill=col);put(d,(103,712),word('В ЭФИРЕ','ON AIR'),40);return im
 if k=='soul':
  im=fit('eyes',W,H).copy(); shift=round(86*math.sin(math.pi*t));ghost=ImageOps.colorize(ImageOps.grayscale(im),'#255249','#c0e8d7');im=Image.blend(im,ghost.transform(im.size,Image.Transform.AFFINE,(1,0,0,0,1,shift)),.35*math.sin(math.pi*t));return im
 if k=='split':
  h=round(460+230*ease(t));im=Image.new('RGB',(W,H),navy);im.paste(fit('monitor',W,670).crop((0,0,W,min(h,670))),(0,0));im.paste(fit('answer',W,820).crop((0,0,W,H-h-8)),(0,h+8));d=ImageDraw.Draw(im);d.rectangle((0,h-52,338,h),fill=navy);put(d,(13,h-46),word('В приёмной','In reception'),32);return im
 p={'names':'desk','check':'producer','resume':'outside','wait':'hiring'}[k];im=Image.new('RGB',(W,H),navy);im.paste(fit(p,W,680),(0,0));d=ImageDraw.Draw(im)
 if k=='names':
  for i,(a,b,c,e) in enumerate([('Гай Кьюни','Guy Kewney','Эксперт','Tech journalist'),('Гай Гома','Guy Goma','Кандидат','Job applicant')]):
   u=min(1,max(0,(t-i*.46)*5));x=int(-665+700*ease(u));y=690+i*94;d.rounded_rectangle((x,y,x+650,y+82),8,fill=cream if i else teal);put(d,(x+14,y+14),word(a,b),36,navy);put(d,(x+310,y+21),word(c,e),27,navy)
 elif k=='check':
  put(d,(39,704),word('Имя','First name'),37);put(d,(338,702),word('Гай','Guy'),42,teal);d.line((40,770,670,770),fill=teal,width=2)
  put(d,(39,791),word('Фамилия','Last name'),37)
  if int(t*6)%2==0:d.rectangle((344,800,350,840),fill=cream)
 elif k=='wait':
  put(d,(40,703),word('До собеседования','Until the job interview'),39);put(d,(39,775),str(round(20*(1-ease(t))))+word(' мин',' min'),59,teal)
 else:
  put(d,(40,698),word('Стрессоустойчивость','Works under pressure'),39);d.rounded_rectangle((40,777,680,830),6,outline=teal,width=3);x=44+int(631*ease(t))
  if x>44:d.rectangle((44,781,x,826),fill=teal)
 return im
