"""Animated inserts for the revised Pepsi episode."""
from functools import lru_cache
from math import sin,pi
from PIL import Image, ImageDraw, ImageOps
from design import bg, panel, font, compose
def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
@lru_cache(None)
def scene(i,size=(720,1280)):
 im=Image.open('new.png').convert('RGB');w,h=im.size
 box=(i%2*w//2+2,i//2*h//2+2,(i%2+1)*w//2-2,(i//2+1)*h//2-2)
 return ImageOps.fit(im.crop(box),size,centering=(.5,.45))
def text(d,xy,msg,n,color,anchor='lm',mono=False):
 d.text(xy,msg,anchor=anchor,font=font(n,mono),fill=color)
steps=['order','balance','purchase','shipping','sock','total']
def receipt(key,u,ru):
 tr=lambda a,b:a if ru else b
 phase=steps.index(key)
 im=bg('blue').copy();d=ImageDraw.Draw(im);paper='#fff3d8';ink='#1c3745';green='#197568';gold='#ffcb71'
 # A single slip extends as each line is printed; entries retain their positions.
 heights=[452,602,744,845,845,945]
 top=210;previous=heights[max(0,phase-1)]
 bottom=round(previous+(heights[phase]-previous)*smooth(u*3))
 if key=='order':
  slide=int(42*(1-smooth(u*3)));top+=slide;bottom+=slide
 panel(d,(29,top-65,694,top+37),'#101e2b',23,'#4d8998')
 panel(d,(48,top-22,672,top+10),'#071523',6)
 d.rectangle((54,top,666,bottom),fill=paper)
 for x in range(54,656,18):d.polygon([(x,bottom),(x+9,bottom+8),(x+18,bottom)],fill=paper)
 text(d,(80,top+50),tr('ЗАКАЗ','ORDER'),44,ink)
 text(d,(641,top+52),'1 × HARRIER',27,green,'rm',True)
 d.line((80,top+92,641,top+92),fill='#a9b8ac',width=2)
 text(d,(81,top+137),tr('Цена в баллах','Price in points'),27,ink)
 text(d,(640,top+178),'7 000 000',50,ink,'rm',True)
 if phase>=1:
  text(d,(82,460),tr('Уже есть','Enclosed'),26,ink)
  for i in range(15):
   if phase==1 and i/20>u:continue
   x=83+i%5*24;y=492+i//5*20
   d.rounded_rectangle((x,y,x+17,y+12),3,fill='#d36c4e')
  text(d,(633,487),'− 15',40,green,'rm',True)
  if phase>1 or u>.44:
   text(d,(82,562),tr('Докупить','Still needed'),24,ink);text(d,(633,558),'6 999 985',43,ink,'rm',True)
 if phase>=2:
  text(d,(83,638),tr('Докупаем','Buy the rest'),26,ink)
  text(d,(635,633),'× $0.10',38,green,'rm',True)
  if phase>2 or u>.25:
   text(d,(82,706),tr('За баллы','Points cost'),24,ink);text(d,(633,704),'$699,998.50',46,ink,'rm',True)
 if phase>=3:
  text(d,(84,795),tr('Доставка','Handling'),28,ink)
  text(d,(634,793),'+ $10.00',38,green,'rm',True)
 if key=='sock':
  inset=scene(2,(295,190)).copy();im.paste(inset,(212,855));d=ImageDraw.Draw(im);d.rectangle((210,853,509,1047),outline=gold,width=5)
 if key=='total':
  panel(d,(61,852,658,939),'#1d645c',12)
  text(d,(359,897),'$700,008.50',59,'#fff8e1','mm',True)
 if phase and bottom<heights[phase]:
  y=bottom+8;im.paste(bg("blue").crop((0,y,720,1280)),(0,y))
 return im
def draw(k,u,ru):
 if k=='deskflip':
  im=compose('agency',0,ru).copy()
  im=Image.blend(im,Image.new('RGB',im.size,'#172636'),.25)
  layer=Image.new('RGBA',(616,180));pd=ImageDraw.Draw(layer)
  a=smooth((u-.47)/.21);front=a<.5
  panel(pd,(3,3,613,176),'#ffe0a4' if front else '#155168',18,'#d3af80')
  text(pd,(309,44),('ПЯТНИЦА' if ru else 'FRIDAY') if front else ('ПОНЕДЕЛЬНИК' if ru else 'MONDAY'),26,'#82482c' if front else '#91d5c2','mm')
  label=(('ГАЗИРОВКА' if ru else 'SODA') if front else ('АВИАСАЛОН' if ru else 'AIRCRAFT SALES'))
  text(pd,(308,108),label,55,'#302e35' if front else '#fff4d5','mm')
  hh=max(4,round(abs(__import__('math').cos(pi*a))*180));layer=layer.resize((616,hh),Image.Resampling.BICUBIC)
  im.paste(layer,(52,790-hh//2),layer)
  return im
 if k in steps:return receipt(k,u,ru)
 if k=='caller':return caller()
 if k in ['ledger','wink']:return scene({'ledger':1,'wink':3}[k])
 if k=='chat':
  im=compose('ocean',0,ru).copy();d=ImageDraw.Draw(im);y=int(685+(1-smooth(u*4))*150)
  panel(d,(67,y,651,y+147),'#182b39',25,'#99d0c0')
  d.ellipse((90,y+37,153,y+100),fill='#c5665b')
  text(d,(122,y+70),'×',39,'white','mm')
  text(d,(175,y+51),'Почки' if ru else 'Kidneys',35,'#faf4e5')
  text(d,(175,y+105),'вышли из чата' if ru else 'left the chat',28,'#a7d8c5')
  return im
 return compose(k,u,ru)

@lru_cache(None)
def caller():
 return ImageOps.fit(Image.open('caller.png').convert('RGB'),(720,1280))
