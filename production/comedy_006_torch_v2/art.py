from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageOps
import math
W,H=720,1280
names='salute whisper prop students flight escort palm speech tram real cheers exam'.split()
@lru_cache(None)
def font(n):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',n)
@lru_cache(None)
def panel(k):
 extra=['late','leave','trousers','guard','script','prof']
 if k in extra:
  im=Image.open('C.png').convert('RGB');w,h=im.width//3,im.height//2;i=extra.index(k);x=i%3*w;y=i//3*h
  return im.crop((x+4,y+4,x+w-4,y+h-4))
 i=names.index(k);im=Image.open('A.png' if i<6 else 'B.png').convert('RGB');w,h=im.width//3,im.height//2;i%=6
 return im.crop((i%3*w+4,i//3*h+4,(i%3+1)*w-4,(i//3+1)*h-4))
ink='#103b3a';cream='#fff1cd';gold='#edb749';red='#ae4036'
@lru_cache(None)
def photo(k):
 if k=='hills':return Image.open('hills.jpg').convert('RGB')
 return panel(k)
@lru_cache(None)
def framed(k,ru):
 if k=='hills':
  im=Image.new('RGB',(W,H),ink);p=photo(k);p.thumbnail((660,760));im.paste(p,((W-p.width)//2,150));d=ImageDraw.Draw(im);d.text((48,178+p.height),'Пэт Хиллс' if ru else 'Pat Hills',font=font(55),fill=cream);return im
 pairs={'salute':'students','whisper':'palm','escort':'students','tram':'speech','real':'salute','cheers':'exam'}
 if k in pairs:
  im=Image.new('RGB',(W,H),ink)
  im.paste(ImageOps.fit(panel(k),(W,848),centering=(.42,.40)),(0,0))
  im.paste(ImageOps.fit(panel(pairs[k]),(W,426),centering=(.5,.34)),(0,854))
  return im
 return ImageOps.fit(panel(k),(W,H),centering=(.50,.45))
animated={'attendance','reverse','tiecheck','peel','cutaway','escorted','grading','inventory','transit','score','close'}
def draw(k,t,ru):
 lang=lambda a,b:a if ru else b
 if k not in animated:return framed(k,ru)
 if k=='close':
  p=panel('escort');w,h=p.size
  return ImageOps.fit(p.crop((.12*w,.04*h,.91*w,.86*h)),(W,H))
 im=Image.new('RGB',(W,H),ink);d=ImageDraw.Draw(im)
 if k in ('attendance','reverse','tiecheck','peel','cutaway','escorted','grading'):
  return gag(k,t,ru)
 if k=='inventory':
  im.paste(ImageOps.fit(panel('prop'),(720,690)),(0,0))
  for i,(a,b) in enumerate([('Ножка стула','Chair leg'),('Банка пудинга','Pudding tin'),('Трусы','Underpants')]):
   if t+0.01>=i*.30:
    y=692+i*69;d.rectangle((0,y,720,y+67),fill=[cream,gold,red][i]);d.text((47,y+6),lang(a,b),font=font(41),fill=ink if i<2 else cream)
 elif k=='transit':
  im.paste(ImageOps.fit(panel('real'),(720,600)),(0,0))
  y=780;d.line((65,y,652,y),fill=gold,width=6)
  x=94+int(505*t);d.rounded_rectangle((x-48,y-58,x+48,y-4),10,fill=red,outline=cream,width=3)
  for i in (-33,-9,15):d.rectangle((x+i,y-48,x+i+16,y-31),fill=cream)
  for e in (-29,29):d.ellipse((x+e-7,y-9,x+e+7,y+5),fill=gold)
  d.text((40,657),lang('Барри уже в трамвае','Barry is already on the tram'),font=font(42),fill=cream)
 else:
  im.paste(ImageOps.fit(panel('exam'),(720,710)),(0,0))
  for i,(a,b,c,e) in enumerate([('Мэр','Mayor','СДАЛ','PASS'),('Экзамен','Exam','ПРОВАЛ','FAIL')]):
   if t+.01>=i*.42:
    y=723+i*83;d.text((42,y),lang(a,b),font=font(43),fill=cream);d.rounded_rectangle((330,y-2,661,y+62),7,fill=red if i else gold);d.text((355,y+2),lang(c,e),font=font(40),fill=cream if i else ink)
 return im
@lru_cache(None)
def poster(k):
 return ImageOps.fit(panel(k),(720,1280))
def gag(k,t,ru):
 word=lambda a,b:a if ru else b
 if k=='reverse':
  im=poster('leave').copy()
  w=int(720*min(1,t*2));im.paste(poster('trousers').crop((0,0,w,1280)),(0,0));d=ImageDraw.Draw(im);d.rectangle((0,760,720,843),fill=ink);d.text((38,770),word('Чуть раньше…','A few minutes earlier…'),font=font(46),fill=cream);return im
 bg={'attendance':'late','tiecheck':'trousers','peel':'palm','cutaway':'prop','escorted':'guard','grading':'prof'}[k]
 im=poster(bg).copy();d=ImageDraw.Draw(im)
 if k=='attendance':
  d.rounded_rectangle((34,690,681,923),20,fill=ink)
  d.text((57,706),word('У ратуши','At Town Hall'),font=font(37),fill=cream)
  for i in range(16):
   x=73+i*38;visible=i<16-int(8*t);col=gold if visible else '#446361'
   d.ellipse((x-8,800,x+8,816),fill=col);d.rounded_rectangle((x-11,820,x+11,862),8,fill=col)
 elif k=='cutaway':
  for i,(a,b) in enumerate([('Ножка стула','Chair leg'),('Банка','Pudding tin')]):
   v=min(1,max(0,t*2-i));x=int(-320+355*v);y=714+i*83
   d.rounded_rectangle((x,y,x+318,y+66),8,fill=ink);d.text((x+15,y+7),word(a,b),font=font(38),fill=cream)
 elif k=='grading':
  for i,(a,b) in enumerate([('Мэр: сдал','Mayor: pass'),('Экзамен: провал','Exam: fail')]):
   if t>=i*.52:
    y=700+i*88;d.rounded_rectangle((45,y,670,y+76),9,fill=ink if not i else red);d.text((66,y+6),word(a,b),font=font(44),fill=cream)
 else:
  text={'tiecheck':('Дресс-код: банк','Dress code: bank'),'peel':('Краска ещё сырая','Paint still wet'),'escorted':('Почётный эскорт','Police escort')}[k]
  w=int(650*min(1,t*3));d.rectangle((34,790,35+w,865),fill=ink)
  if w>550:d.text((50,798),word(*text),fill=cream,font=font(42))
 return im
