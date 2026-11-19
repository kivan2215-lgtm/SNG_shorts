from PIL import Image,ImageOps,ImageDraw,ImageFont
import math
from functools import lru_cache
import numpy as np
W,H=720,1280
@lru_cache(None)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def paper():
 rng=np.random.default_rng(1904); a=rng.normal(0,3,(H,W,1))+np.array([225,210,177]);return Image.fromarray(np.uint8(np.clip(a,0,255)))
panels={'crowd':('A',0),'cramp':('A',1),'ride':('A',2),'break':('A',3),'witness':('A',4),'seat':('A',5),'enter':('B',0),'shoe':('B',1),'wheel':('B',2),'boston':('B',3)}
ink='#263637';red='#8b3830';gold='#e7b35e'
def label(d,x,y,s,n,color=ink):d.text((x,y),s,font=font(n),fill=color)
@lru_cache(None)
def still(k,ru):
 if k in panels:
  sheet,i=panels[k]; im=Image.open('sheet'+sheet+'.png').convert('RGB');w,h=im.width//2,im.height//(3 if sheet=='A' else 2);x=i%2*w;y=i//2*h
  return ImageOps.fit(im.crop((x+2,y+2,x+w-2,y+h-2)),(W,H),centering=(.5,.43))
 im=paper().copy(); d=ImageDraw.Draw(im);pic=Image.open(k+'.jpg').convert('RGB')
 title={'start':('Сент-Луис','St. Louis'),'track':('32 на старте','32 starters'),'lorz':('Фред Лорц','Fred Lorz'),'hicks':('Томас Хикс','Thomas Hicks'),'rest':('После финиша','After the finish'),'cartoon':('Фред Лорц','Fred Lorz')}[k][int(not ru)]
 pw,ph=pic.size; width=692;height=min(850,int(width*ph/pw));width=int(height*pw/ph);x=(W-width)//2;y=510-height//2
 d.line((30,y-18,690,y-18),fill=red,width=4);im.paste(pic.resize((width,height),Image.Resampling.LANCZOS),(x,y));label(d,30,y+height+14,title,44);label(d,30,y+height+73,'1904',25,red);d.line((116,y+height+93,689,y+height+93),fill=red,width=2)
 return im
animated={'route','compare'}
def car(d,x,y,t):
 for xx in (x-28,x+28):
  d.ellipse((xx-12,y-12,xx+12,y+12),fill=ink,outline=gold,width=3)
  for j in range(4):
   a=t*22+j*math.pi/2;d.line((xx,y,xx+8*math.cos(a),y+8*math.sin(a)),fill=gold,width=2)
 d.rounded_rectangle((x-42,y-27,x+43,y-13),4,fill=red);d.rectangle((x+15,y-36,x+35,y-25),fill=red);d.line((x-24,y-42,x-20,y-27,x+4,y-27),fill=ink,width=6)
def runner(d,x,y,t):
 a=math.sin(t*30);d.ellipse((x-4,y-65,x+10,y-51),fill=red);d.line((x+2,y-48,x-5,y-26),fill=ink,width=8)
 for sign in (-1,1):
  d.line((x-5,y-27,x+sign*a*13,y-15,x+sign*a*23,y),fill=ink,width=5);d.line((x,y-43,x-sign*a*12,y-37,x-sign*a*20,y-46),fill=red,width=4)
def flag(d,x,y):
 d.line((x,y-75,x,y+10),fill=ink,width=4)
 for r in range(3):
  for c in range(5):d.rectangle((x+c*6,y-75+r*6,x+c*6+6,y-69+r*6),fill=ink if (c+r)%2 else '#faf2dd')
def draw(k,t,ru):
 if k not in animated:return still(k,ru)
 im=paper().copy();d=ImageDraw.Draw(im);word=lambda a,b:a if ru else b
 d.line((42,265,678,265),fill=red,width=4)
 label(d,42,284,word('Дистанция Лорца','Lorz’s race') if k=='route' else word('Кого подвезли?','Who caught a ride?'),50)
 if k=='route':
  for i,(a,b) in enumerate([('Пешком','On foot'),('На машине','By car'),('Снова бегом','On foot again')]):
   y=445+i*145;label(d,46,y-58,str(i+1).zfill(2),23,red);label(d,99,y-71,word(a,b),32);d.line((82,y+12,642,y+12),fill='#988972',width=3)
   u=min(1,max(0,t*3-i));d.line((82,y+12,82+535*u,y+12),fill=red,width=5)
   (car if i==1 else runner)(d,91+514*u,y,t if 0<u<1 else 0)
  flag(d,642,735)
 else:
  for i,(a,b,c,e) in enumerate([('Лорц','Lorz','до финиша','before the finish'),('Хикс','Hicks','после финиша','after the finish')]):
   y=500+i*212; label(d,46,y-100,word(a,b),40);label(d,46,y+25,word(c,e),30,red)
   d.line((55,y+4,660,y+4),fill=ink,width=3);flag(d,378,y);car(d,(100 if not i else 431)+min(1,max(0,t*2-i))*166,y,t)
 return im
